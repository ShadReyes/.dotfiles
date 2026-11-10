#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
for python in python3 python3.14 python3.13 python3.12 python3.11; do
  if command -v "$python" >/dev/null 2>&1 &&
    "$python" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
    exec "$python" - "$DOTFILES" "$@" <<'PY'
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(sys.argv.pop(1))
REAL_PYTHON = sys.executable
REAL_GIT = shutil.which("git")
if REAL_GIT is None:
    raise SystemExit("Git is required for isolated bootstrap tests")


def executable(path, text):
    path.write_text(text)
    path.chmod(0o755)


@contextlib.contextmanager
def fixture(runtime="supported", platform="linux", git_available=True):
    with tempfile.TemporaryDirectory(prefix="skillset-bootstrap-") as temporary:
        root = Path(temporary).resolve()
        repo = root / "checkout with spaces"
        home = root / "home"
        bin_dir = root / "bin"
        repo.mkdir()
        home.mkdir()
        bin_dir.mkdir()
        # Isolate host interpreter/package availability, retaining real Unix tools.
        excluded = {"brew", "curl", "apt-get", "sudo", "stow", "herdr", "jq", "npm"}
        for directory in (Path("/usr/bin"), Path("/bin")):
            for command in directory.iterdir():
                destination = bin_dir / command.name
                if (command.name.startswith(("python", "git")) or command.name in excluded
                        or destination.exists() or destination.is_symlink()):
                    continue
                if command.is_file() and os.access(command, os.X_OK):
                    destination.symlink_to(command)

        for name in ("bootstrap.sh", "Brewfile", "sync-skills.sh", "sync-pi.sh"):
            shutil.copy2(ROOT / name, repo / name)
        (repo / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/skillset", repo / "scripts/skillset")
        shutil.copytree(ROOT / "scripts/skillset_lib", repo / "scripts/skillset_lib",
                        ignore=shutil.ignore_patterns("__pycache__"))

        skill = repo / "skills/sample"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: sample\ndescription: Fixture skill\n---\n\nFixture.\n")
        (repo / "agents").mkdir()
        (repo / "agents/sample.toml").write_text(
            'name = "sample"\ndescription = "Fixture agent"\n'
            'developer_instructions = """\nFixture instructions.\n"""\n')
        (repo / "commands").mkdir()
        (repo / "commands/sample.md").write_text("Fixture command.\n")
        (repo / "skillset").mkdir()
        documents = {
            "catalog.json": {"schema_version": 1,
                             "sources": {
                                 "sample-source": {"type": "directory", "path": "skills/sample",
                                                   "provenance": "authored"},
                                 "remote-source": {"type": "git", "url": "https://example.test/skills.git",
                                                   "ref": "main", "provenance": "third-party"}},
                             "skills": {"sample": {"source": "sample-source", "path": "."},
                                        "remote-sample": {"source": "remote-source", "path": "."}}},
            "profiles.json": {"schema_version": 1, "profiles": {}},
            "lock.json": {"schema_version": 1, "sources": {}},
        }
        for name, value in documents.items():
            (repo / "skillset" / name).write_text(json.dumps(value))

        log = root / "calls"
        log.touch()
        env = {
            "HOME": str(home), "PATH": str(bin_dir), "LC_ALL": "C",
            "TMPDIR": str(root), "DOTFILES_OS": platform,
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local/share"),
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file",
            "SKILLSET_TEST_LOG": str(log), "SKILLSET_TEST_BIN": str(bin_dir),
            "SKILLSET_TEST_PYTHON": REAL_PYTHON, "SKILLSET_TEST_GIT": REAL_GIT,
        }

        (bin_dir / "git").symlink_to(REAL_GIT)
        def git(*args):
            return subprocess.run([REAL_GIT, *args], env=env, check=True,
                                  text=True, capture_output=True)

        # Real local repositories ensure unchanged legacy submodule sync is exercised
        # without network access or touching the user's checkout/submodules.
        package_source = root / "package-source"
        git("init", "-q", str(package_source))
        (package_source / "index.ts").write_text("export {};\n")
        git("-C", str(package_source), "add", ".")
        git("-C", str(package_source), "-c", "user.name=Fixture Builder", "-c",
            "user.email=fixture@example.test", "commit", "-qm", "Fixture package")
        git("init", "-q", str(repo))
        git("-C", str(repo), "-c", "protocol.file.allow=always", "submodule", "add", "-q",
            str(package_source), "pi/orca-pi")
        (bin_dir / "git").unlink()

        # These doubles stand only at external package-manager/download boundaries.
        for name in ("brew", "apt-get", "curl"):
            executable(bin_dir / name, '''#!/usr/bin/env bash
set -euo pipefail
name="$(basename "$0")"
printf '%s %s\n' "$name" "$*" >> "$SKILLSET_TEST_LOG"
if [ "${SKILLSET_TEST_ALLOW_INSTALL:-0}" != 1 ]; then
  echo "Unexpected package install or download" >&2
  exit 91
fi
case "$name:$1" in
  brew:bundle|apt-get:install) ln -sf "$SKILLSET_TEST_PYTHON" "$SKILLSET_TEST_BIN/python3" ;;
  apt-get:update) ;;
  *) echo "Unexpected download" >&2; exit 92 ;;
esac
''')
        executable(bin_dir / "sudo", '''#!/usr/bin/env bash
set -euo pipefail
printf 'sudo %s\n' "$*" >> "$SKILLSET_TEST_LOG"
if [ "$1" = -n ] && [ "$2" = true ]; then exit 0; fi
exec "$@"
''')
        for name in ("stow", "herdr", "jq", "npm"):
            executable(bin_dir / name, '#!/usr/bin/env bash\nexit 0\n')
        if git_available:
            executable(bin_dir / "git", '''#!/usr/bin/env bash
set -euo pipefail
printf 'git %s\n' "$*" >> "$SKILLSET_TEST_LOG"
exec "$SKILLSET_TEST_GIT" "$@"
''')
        if runtime == "supported":
            (bin_dir / "python3").symlink_to(REAL_PYTHON)
        elif runtime == "versioned":
            # This double stands at the unsupported host interpreter boundary.
            executable(bin_dir / "python3", '#!/usr/bin/env bash\nexit 1\n')
            (bin_dir / "python3.11").symlink_to(REAL_PYTHON)
        elif runtime == "old":
            executable(bin_dir / "python3", '#!/usr/bin/env bash\nexit 1\n')
        elif runtime != "missing":
            raise AssertionError(runtime)
        # Avoid unrelated Oh My Zsh provisioning in package-runtime tests.
        (home / ".oh-my-zsh").mkdir()
        (home / ".oh-my-zsh/oh-my-zsh.sh").touch()
        yield repo, home, bin_dir, log, env


def bootstrap(repo, env, flag="--stow-only"):
    return subprocess.run([str(repo / "bootstrap.sh"), flag], env=env,
                          cwd=repo.parent, text=True, capture_output=True)


class SkillsetBootstrapTests(unittest.TestCase):
    def assert_no_manager_state(self, home):
        self.assertFalse((home / ".config/skillset").exists())
        self.assertFalse((home / ".local/share/skillset").exists())

    def assert_no_downloads(self, log):
        self.assertFalse(any(line.startswith(("brew ", "curl ", "apt-get ", "sudo "))
                             for line in log.read_text().splitlines()), log.read_text())
        self.assertNotIn(" clone ", log.read_text())
        self.assertNotIn(" fetch ", log.read_text())

    def test_skip_packages_links_working_cli_without_selecting_or_installing(self):
        with fixture() as (repo, home, bin_dir, log, env):
            result = bootstrap(repo, env)

            self.assertEqual(result.returncode, 0, result.stderr)
            link = home / ".local/bin/skillset"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), repo / "scripts/skillset")
            self.assertIn("skillset runtime ready:", result.stdout)
            self.assert_no_downloads(log)
            self.assert_no_manager_state(home)
            # The real CLI imports its repository package through the symlink, from
            # an unrelated cwd; a registered but unselected skill stays uninstalled.
            cli_env = dict(env, PATH=str(home / ".local/bin") + ":" + str(bin_dir))
            listed = subprocess.run([str(link), "list", "--json"], env=cli_env,
                                    cwd=home, text=True, capture_output=True)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("sample", listed.stdout)
            self.assertEqual(json.loads(listed.stdout)["schema_version"], 1)
            resolved = subprocess.run([str(link), "resolve", "--json"], env=cli_env,
                                      cwd=home, text=True, capture_output=True)
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            self.assertEqual(json.loads(resolved.stdout)["selected"], [])
            self.assertEqual(json.loads(resolved.stdout)["active"], [])
            self.assert_no_manager_state(home)
            self.assertTrue((home / ".claude/skills/sample").is_symlink())
            self.assertTrue((home / ".agents/skills/sample").is_symlink())
            self.assertTrue((home / ".codex/agents/sample.toml").is_symlink())
            self.assertIn("Fixture instructions.", (home / ".claude/agents/sample.md").read_text())
            self.assertTrue((home / ".claude/commands/sample.md").is_symlink())
            self.assertTrue((home / ".pi/agent/extensions/orca-pi").is_symlink())

    def test_skip_packages_reports_missing_or_old_python_without_downloads(self):
        for runtime, flag in (("missing", "--stow-only"), ("old", "--no-packages")):
            with self.subTest(runtime=runtime), fixture(runtime=runtime) as (repo, home, _, log, env):
                result = bootstrap(repo, env, flag)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("skillset is unavailable: missing Python 3.11+", result.stderr)
                self.assertIn("without downloading prerequisites", result.stderr)
                self.assertIn("brew install python git", result.stderr)
                self.assertIn("apt-get install python3 git", result.stderr)
                self.assertTrue((home / ".local/bin/skillset").is_symlink())
                self.assertTrue((home / ".claude/skills/sample").is_symlink())
                self.assert_no_downloads(log)
                self.assert_no_manager_state(home)

    def test_versioned_python_fallback_works_with_unsupported_python3(self):
        with fixture(runtime="versioned") as (repo, home, bin_dir, log, env):
            result = bootstrap(repo, env)
            cli = subprocess.run([str(home / ".local/bin/skillset"), "list", "--json"],
                                 env=env, cwd=home, text=True, capture_output=True)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("skillset runtime ready:", result.stdout)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertIn("sample", cli.stdout)
            self.assert_no_downloads(log)
            self.assert_no_manager_state(home)

    def test_missing_git_is_reported_before_legacy_git_requirement_fails(self):
        with fixture(git_available=False) as (repo, home, _, log, env):
            result = bootstrap(repo, env, "--no-packages")

            # Git was already required by legacy sync-pi; skip mode does not turn
            # that pre-existing requirement into a successful installation.
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("skillset is unavailable: missing Git on PATH", result.stderr)
            self.assertIn("without downloading prerequisites", result.stderr)
            self.assert_no_downloads(log)
            self.assert_no_manager_state(home)

    def test_existing_unrelated_executable_directory_and_links_are_not_replaced(self):
        for kind in ("executable", "directory", "symlink", "broken-symlink"):
            with self.subTest(kind=kind), fixture() as (repo, home, _, log, env):
                link = home / ".local/bin/skillset"
                link.parent.mkdir(parents=True)
                if kind == "executable":
                    executable(link, "#!/bin/sh\nprintf 'unrelated-command\\n'\n")
                elif kind == "directory":
                    link.mkdir()
                    (link / "keep").write_text("preserved")
                else:
                    other = home / "other-command"
                    if kind == "symlink":
                        executable(other, "#!/bin/sh\nexit 0\n")
                    link.symlink_to(other)
                original_inode = link.lstat().st_ino

                result = bootstrap(repo, env)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(link.lstat().st_ino, original_inode)
                self.assertIn("Not replacing existing", result.stderr)
                self.assertIn("Move that path aside manually", result.stderr)
                if kind == "executable":
                    self.assertIn("unrelated-command", link.read_text())
                elif kind == "directory":
                    self.assertEqual((link / "keep").read_text(), "preserved")
                else:
                    self.assertEqual(os.readlink(link), str(home / "other-command"))
                self.assert_no_downloads(log)

    def test_repeated_bootstrap_preserves_its_existing_cli_link(self):
        with fixture() as (repo, home, _, log, env):
            first = bootstrap(repo, env)
            self.assertEqual(first.returncode, 0, first.stderr)
            link = home / ".local/bin/skillset"
            original_inode = link.lstat().st_ino

            second = bootstrap(repo, env)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(link.lstat().st_ino, original_inode)
            self.assertIn("skillset CLI already linked", second.stdout)
            self.assert_no_downloads(log)
            self.assert_no_manager_state(home)

    def test_supported_package_paths_provision_python_before_runtime_check(self):
        for platform in ("macos", "linux"):
            with self.subTest(platform=platform), fixture(runtime="missing", platform=platform) as (repo, home, _, log, env):
                env["SKILLSET_TEST_ALLOW_INSTALL"] = "1"

                result = bootstrap(repo, env, "--packages")

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("skillset runtime ready:", result.stdout)
                calls = log.read_text()
                if platform == "macos":
                    self.assertIn("brew bundle --file=", calls)
                    self.assertRegex((repo / "Brewfile").read_text(), r'(?m)^brew "python"')
                    self.assertRegex((repo / "Brewfile").read_text(), r'(?m)^brew "git"')
                    self.assertNotIn("apt-get ", calls)
                else:
                    self.assertIn("sudo apt-get update", calls)
                    self.assertRegex(calls, r"apt-get install [^\n]*\bpython3\b")
                    self.assertRegex(calls, r"apt-get install [^\n]*\bgit\b")
                    self.assertNotIn("brew ", calls)
                self.assert_no_manager_state(home)

    def test_package_mode_rejects_an_unsatisfied_runtime(self):
        with fixture(runtime="missing") as (repo, home, bin_dir, log, env):
            # The native package-manager boundary can report success on a distro
            # whose default Python is still too old; bootstrap must not claim ready.
            executable(bin_dir / "apt-get", "#!/usr/bin/env bash\nexit 0\n")

            result = bootstrap(repo, env, "--packages")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing Python 3.11+", result.stderr)
            self.assertNotIn("skillset runtime ready:", result.stdout)
            self.assertFalse((home / ".local/bin/skillset").exists())
            self.assert_no_manager_state(home)


unittest.main()
PY
  fi
done

echo 'Python 3.11+ is required for isolated bootstrap tests.' >&2
exit 1

---
name: mintlify-cli
description: Use when working with the Mintlify documentation CLI, including previewing, validating, exporting, checking links or accessibility, managing CLI configuration, analytics, authentication, scaffolding, or diagnosing command/version differences.
---

# Mintlify CLI

Use the installed `mint` command for Mintlify documentation work. The command
reference is the source of truth for syntax and flags:

<https://www.mintlify.com/docs/cli/commands.md>

## Before running a command

1. Confirm the command available on this machine:

   ```bash
   mint version
   mint --help
   mint <command> --help
   ```

2. Consult the official command reference for the requested operation. The
   online docs can describe commands or flags that are newer than the locally
   installed CLI.
3. Run commands from the Mintlify documentation repository, normally the
   directory containing `docs.json`.

Prefer the local CLI's help when it conflicts with the online reference. Report
the version difference and suggest `mint update` (or reinstalling `mint@latest`)
when the requested command is unavailable locally.

## Common workflows

- Preview changes: `mint dev` (use `--no-open` in automation or headless shells).
- Validate a build: `mint validate`.
- Check internal links: `mint broken-links`; add `--check-anchors`,
  `--check-redirects`, `--check-snippets`, or `--check-external` when needed.
- Check accessibility: `mint a11y`.
- Export an offline site: `mint export --output <file>`.
- Check agent readiness for a public site: `mint score [url]`.
- View or change persistent CLI settings: `mint config get|set|clear`.
- View analytics when supported by the installed CLI: `mint analytics ...`.

For OpenAPI-backed docs, use the OpenAPI options documented for `mint validate`
or `mint dev`. Treat the deprecated standalone `mint openapi-check` command as a
fallback only when the local CLI still exposes it.

## Safety and authentication

- Do not run `mint login`, `mint logout`, or commands that change persistent
  configuration unless the user requests that action.
- Never expose credentials from Mintlify config files or pass secrets on the
  command line.
- Do not use `mint new --force` without explicit confirmation; it can overwrite
  an existing documentation directory.
- Do not enable external-link checks by default in offline or restricted
  environments; they require network access.
- Mention telemetry when relevant. The CLI supports `--telemetry false`, and
  `MINTLIFY_TELEMETRY_DISABLED=1` or `DO_NOT_TRACK=1` can disable it.

## Completion

Report the exact command run, its relevant output or failure, and the local CLI
version. If the task changed files, identify them and run the narrowest relevant
validation command before handing off.

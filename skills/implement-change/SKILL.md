---
name: implement-change
description: Implement a requested repository change with explicit project-context discovery, relevant skill loading, scoped edits, and proportional verification. Use when the user asks to build, change, fix, add, update, or implement code or documentation in a repository, especially when another workflow skill delegates implementation.
---

# Implement Change

Use this skill as the implementation phase for repository work. It coordinates context and validation; specialist skills remain authoritative for domain-specific code, tests, APIs, jobs, views, and tooling.

## Before editing

1. Identify the repository and active worktree. Do not make changes in a main or otherwise unrelated worktree when an isolated worktree is available or required.
2. Read repository-local instructions before taking action, including `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, and equivalent files. The nearest applicable instruction wins; preserve unrelated user changes.
3. Inspect the branch and working tree. Determine the smallest file set that can satisfy the request.
4. Identify every relevant project skill from the available skill catalog using the requested behavior and the files likely to change. Read each selected `SKILL.md` completely before editing. If a selected skill references a required guide, load that guide before acting.
5. Announce the selected skills and why they apply. A parent workflow skill does not replace project skills: for example, a PR-comment workflow still loads `rails-tests` when changing a test and `openapi-contract` when changing an API contract.

## Skill selection signals

Load the narrowest set that covers the change. Common signals include:

- `test/**/*_test.rb` → `rails-tests`; API integration tests also require the repository's OpenAPI/Skooma guidance.
- `app/models/` or `test/models/` → `rails-models`, plus a more specific service, money, state-machine, search, or database skill when applicable.
- `app/services/` or domain logic → `rails-services` or `rails-refactoring` as applicable.
- controllers, routes, params, serializers, Blueprinters, or API specs → `rails-controllers`, `openapi-contract`, and any serialization/validation skill indicated by the files.
- jobs, mailers, or rake tasks → `rails-jobs` and `sidekiq` when queue behavior is involved.
- views or themes → `rails-views` or `themes`.
- frontend TypeScript/React → the relevant project frontend skill and the applicable doctor skill after edits.

These are routing hints, not an exhaustive list. Search the repository's instruction index and available skills for more specific matches. User-named skills are mandatory.

## Implement

- Follow the selected project skills and repository instructions over surrounding legacy precedent.
- Keep the diff focused. Do not perform unrelated cleanup or architectural changes unless required by the request or the selected skill.
- Preserve existing user changes and inspect overlapping diffs before editing.
- Prefer the repository's documented edit tool and execution environment. For Rails projects, route Ruby, Bundler, Rails, and Rake commands through the required container or devcontainer.
- Treat missing dependencies, failing infrastructure, or ambiguous scope as verification facts to report, not reasons to silently weaken the implementation.

## Verify and hand off

1. Inspect the final diff and run `git diff --check`.
2. Run the relevant formatter/linter on changed files.
3. Run the narrowest relevant tests, then expand only when risk warrants it.
4. Re-check the selected skill checklists. For API tests, confirm status assertions precede Skooma conformance assertions, successful responses use `assert_conform_schema`, JSON requests use `as: :json`, and documented exceptions are explicit.
5. Report changed files, verification results, and blockers. Do not commit, push, open PRs, reply externally, or modify external systems unless the user requested it or the parent workflow explicitly includes that action.

Parent workflow skills may invoke this skill for implementation and then continue with their own commit, review, publishing, or communication steps.

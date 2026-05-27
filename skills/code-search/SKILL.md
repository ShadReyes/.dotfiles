---
name: code-search
description: Semantic code search for large repo exploration, feature planning, codebase discovery, or when user explicitly requests semantic search. Triggers on tasks involving understanding unfamiliar codebases, planning multi-file changes, or finding code by behavior/purpose.
---

# code-search — Semantic Code Search

## When to use

- Medium-to-complex tasks in repos with **100+ files**
- Exploring unfamiliar codebases or discovering related code across modules
- Feature planning that requires finding all relevant touchpoints
- User explicitly asks to use semantic search
- When Grep/Glob would require guessing at naming conventions

**Skip** for simple/well-scoped changes where target files are already known.

## Prerequisites

1. **Ollama running:** `ollama serve` (or check `curl -s http://localhost:11434/api/tags`)
2. **Repo indexed:** Run `npx tsx ~/Documents/code-search/src/index.ts index --full --repo <path>`
3. **Check index:** `npx tsx ~/Documents/code-search/src/index.ts stats --repo <path>`

## CLI reference

All commands: `npx tsx ~/Documents/code-search/src/index.ts <command> --repo <path>`

| Command | Flags | Purpose |
|---------|-------|---------|
| `init` | | Create config in repo |
| `index` | `--full`, `--verbose` | Build/rebuild search index |
| `query "<search>"` | `--limit N`, `--filter <path>` | Semantic search |
| `stats` | | Show index info |

- `--repo <path>` or set `CODE_SEARCH_REPO` env var to avoid repeating the path

## Recommended workflow

1. **Semantic search first** — Run 2-5 broad queries to discover relevant files and code regions
2. **Scope with `--filter`** — Narrow results to relevant directories (e.g., `--filter src/api`)
3. **Use `--limit 10`** — When exploring broadly, request more results
4. **Then Grep/Glob/Read** — Once you know the files, switch to precise tools for detailed examination

This workflow gives ~15-25% token/time savings on medium-to-complex tasks vs. Grep/Glob alone.

## Query writing tips

Natural language describing **behavior or purpose** works best:

- Describe behavior: `"authentication middleware that checks JWT tokens"`
- Describe role: `"React hook for managing user session state"`
- Describe pattern: `"POST handler for creating invoices"`
- Describe intent: `"error handling for database connection failures"`

Avoid overly specific symbol names — use those with Grep instead.

## When NOT to use

- Simple single-file changes where you know the target
- Repo is small (<50 files) — Grep/Glob is faster
- Searching for exact symbol names or string literals — use Grep
- Index is stale and re-indexing would take longer than manual search

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Connection refused" on query/index | Start Ollama: `ollama serve` |
| No results or poor results | Re-index: `index --full --repo <path>` |
| Missing model | `ollama pull nomic-embed-text` |
| Stale results after code changes | Re-index (incremental is default, use `--full` if needed) |

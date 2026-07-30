---
name: mist-agent-control
description: Drive Mist Desktop's full agent (all tools, skills, workflows) from an external harness like Claude Code or Codex via its local HTTP agent-control server, instead of the desktop UI. Use when asked to run a Mist turn, skill, or workflow headlessly/from the terminal, to script Mist flows, or to test Mist behavior without clicking through the app.
user-invocable: true
---

# Mist Agent Control (drive Mist from an external harness)

Mist Desktop embeds its entire agent loop in the Electron **main** process and exposes a
dev-only, token-authenticated HTTP server on loopback that fires real agent turns —
identical to typing in the chat UI. A turn started over HTTP gets the full Mist agent:
all ~65 built-in tools, community/local skills, workflows, safe mode, and evidence
receipts. Chat history, activity, and receipts land in normal Mist state.

Source of truth (fluid-mono):
`apps/mist-desktop/src/main/services/agent-control-server.service.ts`

## Setup (one time per session)

1. Mist must run **from source** (dev build). From `fluid-mono/apps/mist-desktop`:

   ```bash
   MIST_AGENT_CONTROL_ENABLED=1 \
   MIST_AGENT_CONTROL_TOKEN='<any secret ≥20 chars>' \
   pnpm start
   ```

   Optional: `MIST_AGENT_CONTROL_PORT` (default `9846`), `MIST_AGENT_CONTROL_ROOT`
   (path jail for projects, default `~/Fluid`).

2. Sign in to the target company **in the Mist UI** (email + MFA). There is no login
   endpoint; turns fail with "requires a signed-in company" otherwise.

3. Verify: `curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:9846/v1/health`
   → `{"ok":true}`.

## API

All requests need `Authorization: Bearer <token>`. Loopback only.

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/health` | Liveness check |
| POST | `/v1/turns` | Start a turn → `202` + record with `requestId`, `chatId` |
| GET | `/v1/turns/:requestId` | Poll status: `queued` → `running` → `succeeded` / `failed` / `aborted` |
| POST | `/v1/turns/:requestId/abort` | Abort a queued/running turn |
| POST | `/v1/companies/activate` | `{companySlug}` → switch active signed-in profile (aborts all turns, stops CLI processes) |
| POST | `/v1/themes` | `{name, companySlug}` → scaffold a new theme project |

### Start-turn body

```json
{
  "projectId": "theme-123",
  "projectName": "My Theme",
  "projectKind": "theme",
  "projectPath": "/Users/you/Fluid/<companySlug>/themes/my-theme",
  "text": "Run the accessibility audit and summarize findings.",
  "title": "a11y audit",
  "chatId": "chat-...",
  "skillSlug": "themes/accessibility-audit",
  "companySlug": "acme",
  "model": "anthropic/claude-sonnet-5",
  "readOnly": false
}
```

- `projectKind`: `theme | portal | widget | mist | skill | mysite`.
- `chatId` (optional) continues an existing chat; must already exist in the project and
  match `^chat-[A-Za-z0-9-]+$`. Omit to create a fresh chat (optionally titled `title`).
- `skillSlug` (optional) pre-activates a Mist skill for the turn (same as the `/` picker).
- `companySlug` (optional) pins the turn to a signed-in company profile; otherwise the
  active profile is used.
- `readOnly: true` strips all mutation tools (the workflow-QA allowlist).

### Getting the result

The turn record contains **only status/`turnId`/`error` — never the assistant's output**.
Read the transcript from disk once status is terminal:

```
<projectPath>/.mist-desktop/chats/index.json      # chat list
<projectPath>/.mist-desktop/chats/<chatId>.json   # full message log incl. tool calls
```

Poll pattern:

```bash
REQ=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d @turn.json http://127.0.0.1:9846/v1/turns)
ID=$(jq -r .requestId <<<"$REQ"); CHAT=$(jq -r .chatId <<<"$REQ")
until curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:9846/v1/turns/$ID" \
  | jq -e '.status | IN("succeeded","failed","aborted")' >/dev/null; do sleep 5; done
jq '.messages[-1]' "<projectPath>/.mist-desktop/chats/$CHAT.json"
```

## Finding projects and IDs

There is **no project-listing endpoint**. Projects live under
`~/Fluid/<companySlug>/{themes,portals,mist,widgets}/<name>`. Use the renderer's ID
format so the UI, abort, and live-turn snapshots agree:

| Kind | ID format | Derived from |
|---|---|---|
| theme | `theme-<themeId>` | `.fluid-theme.json` → `themeId` (number) |
| mist | `mist-<slug>` | `.mist` → `slug` |
| portal | `portal-<dirname>` | directory name (no marker file yet) |
| widget | `widget-<dirname>` | directory name (`fluid.widget.config.ts` present) |

## Running skills and workflows

- **Skill**: pass `skillSlug` (e.g. `finance/promo-code-summary`) plus a short `text`
  kicking it off. Slugs come from the mist-skills manifest or `~/Fluid/skills/`.
- **Workflow**: there is no dedicated endpoint. Start a turn whose `text` asks the agent
  to run it (the agent calls the `run_workflow` tool), e.g.
  `"Run the onboard-launch-company workflow for https://example.com with run_scope=theme_only"`.
  Progress is visible in the Mist UI and via `workflow_status` in follow-up turns; run
  state persists under Electron `userData/workflows/<runId>.json`.

## Limitations (as of mist-desktop 0.32.0)

- **Dev builds only.** The server starts only when the app is unpackaged and throws if
  `NODE_ENV=production`. You cannot drive the installed/packaged Mist app.
- **Not headless.** Mist (full Electron app, window and all) must be running; the API
  rides on the live process. If Mist quits, the server dies and all turn records vanish
  (they're in-memory; only the last 100 completed are kept even while running).
- **Sign-in is UI-only.** Email+MFA login has no API; the target company must already be
  signed in. `companySlug` can only select among already-signed-in profiles.
- **No output or streaming over HTTP.** Poll for terminal status, then read the chat
  JSON from disk. No SSE/WebSocket, no token/cost/telemetry in the API.
- **Human-in-the-loop stalls.** Tools like `human_in_the_loop`, `steps`, and UI cards
  render only in the Mist window; the API cannot answer them. A turn that asks a
  question waits until someone answers in the UI — write self-sufficient prompts
  (state defaults and choices up front) for unattended runs.
- **Path jail.** `projectPath` is realpath-resolved and must be strictly *inside*
  `MIST_AGENT_CONTROL_ROOT` (default `~/Fluid`); the root itself and symlinks escaping
  it are rejected.
- **No discovery.** Can't list projects, chats, companies, skills, or workflow runs over
  HTTP — derive them from the filesystem (see above).
- **Caller-supplied identity.** `projectId`/`projectName` are trusted strings; a
  mismatched `projectId` breaks abort and live-turn dedup against UI-started turns.
- **Scaffolding is themes-only.** `/v1/themes` exists; portals/widgets/mist apps must be
  created in the UI (or by an agent turn) first.
- **Caps.** ≤20 concurrent turns (429 above that), request bodies ≤256KB, `text`
  ≤200k chars, token ≥20 chars, binds 127.0.0.1 only (other hosts refused at startup).
- **Shared state with the UI.** API turns write the same chats the UI shows. That's the
  point — but avoid firing into a chat a human is actively using.
- **Undocumented surface.** No `.env.local.example` entries, no upstream docs or client;
  behavior is defined by the source file and its test. Re-check the source after Mist
  upgrades.

## Troubleshooting

- `401` → token mismatch (compare with the env var Mist was launched with).
- `400 "Project path is outside the configured Fluid root"` → check
  `MIST_AGENT_CONTROL_ROOT` and symlinks (path is realpath'd).
- `400 "No unique signed-in company profile matches …"` → sign in to that company in the
  UI, or omit `companySlug` to use the active profile.
- Connection refused → Mist not running from source, env vars missing, or port taken
  (set `MIST_AGENT_CONTROL_PORT`).
- Turn `failed` with a terse `error` → open the chat in the Mist UI; full context is in
  the transcript and `<userData>/.devtools` traces when `MIST_AI_DEVTOOLS=1`.

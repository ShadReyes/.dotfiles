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

## Tool bridge — call Mist's tools directly, no model turn

The same server can expose Mist's **individual agent tools** as one HTTP call each, with
no agent turn in between. Use this when you want `fluid_api`, `db_query`,
`screenshot_preview`, `crawl`, … as native tools in *your* harness; use `/v1/turns`
(above) when you want Mist's model to reason.

Source: `apps/mist-desktop/src/main/services/tool-bridge.service.ts`,
`src/main/tools/bridge-policy.ts`, `src/shared/tool-bridge.ts`.

Every call still goes through `buildTools`, so it inherits Safe Mode, the project
sandbox, Time Machine recording, and signed evidence receipts unchanged.

### Enabling

Second gate on top of agent control — **off by default even when agent control is on**:

```bash
MIST_AGENT_CONTROL_ENABLED=1 \
MIST_BRIDGE_ENABLED=1 \
MIST_AGENT_CONTROL_TOKEN='<secret ≥20 chars>' \
MIST_BRIDGE_ALLOWED_COMPANIES=hiya-health-test-2 \
pnpm start
```

| Var | Default | Effect |
|---|---|---|
| `MIST_BRIDGE_ENABLED` | unset | `=1` mounts `/v1/tools*` (needs `MIST_AGENT_CONTROL_ENABLED=1` too) |
| `MIST_BRIDGE_ALLOW_WRITES` | unset | `=1` permits calls classified as production mutations. **Does not defeat Safe Mode** — that still refuses inside `buildTools` |
| `MIST_BRIDGE_ALLOWED_COMPANIES` | unset | Comma-separated companies. Each entry may be the profile display name (`Hiya Health Test 2`), the storefront slug (`hiya-health-test-2`), or the `*.fluid.app` host — both sides are normalized through Mist's own `slugifyCompany` / `slugifyFluidShop`, so the spellings are interchangeable. **Fails closed**: set-but-empty blocks everything, and there is no active-profile fallback |
| `MIST_BRIDGE_TOOLS` | unset | Comma-separated tool allowlist; when set, only these are exposed |
| `MIST_BRIDGE_MAX_OUTPUT_BYTES` | `16384` | Output cap before truncation |
| `MIST_BRIDGE_DEFAULT_WAIT_MS` | `55000` | Long-poll budget before a call switches to job mode |

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/tools` | Catalog. `?readOnly=1` for the QA-reviewer tool semantics; `?includeUnavailable=0` to hide tools the current flags refuse (default is to list them **with** the env var that would unlock each) |
| POST | `/v1/tools/invoke` | Run one tool. `200` when it finishes inside `waitMs`, `202` + `invocationId` when it does not |
| GET | `/v1/tools/invocations/:id` | Poll a job |
| POST | `/v1/tools/invocations/:id/abort` | Abort it (`409` if already terminal) |

Invoke body: `{tool, args, projectPath?, projectId?, projectName?, projectKind?,
connectionId?, companySlug?, readOnly?, waitMs?, images?, clientId?}`. `projectPath` is
path-jailed exactly like `/v1/turns`; omit it and the sandbox roots at the workspace.
`connectionId` overrides `projectInfo.id` for `db_query` / `db_schema` /
`sql_answer_card`, which resolve their database from it. `images` defaults to `"paths"`
(you read the PNG off disk); `"inline"` returns base64, capped at 2 images / 1.5MB.

Response: `{invocationId, tool, status, output, isError, truncated?, images?,
historyEntryIds?, surfaceReceiptId?, error?}`. **`historyEntryIds` are Time Machine
entries** — hand one back to Mist to revert the mutation.

Status codes: policy refusals are **`200` with `status:"refused"`** on purpose (a model
must read the reason and adapt, not see a transport error). Only `404` unknown tool,
`400` bad args / path-jail violation, `429` over the 8-invocation cap, `501` bridge off.

### Exposed surface

65 of Mist's 68 tools. Never exposed, each with a refusal naming the alternative:

- `create_page` — gated on per-turn facts only the chat history can prove. Use `/v1/turns`.
- `steps` — means "end your turn and wait for the human". Use `/v1/turns`.
  (`steps_answer` / `steps_mark_item` *are* exposed.)
- `send_message` — fires a nested agent turn in another project. Use `/v1/turns` there.
- Any `mcp__*` tool — proxying Mist's own MCP servers back out would bypass their consent.

Write classification reuses Safe Mode's audited `checkSafeModeTool`, so it is
argument-sensitive: `fluid_api` GET is allowed while POST is not, `theme_media_reconcile`
with `verify_only:true` is allowed, `run_cli git status` is allowed while
`run_cli fluid theme push` is not.

### Registering the MCP proxy

`packages/mist/mcp` ships a second binary, `mist-bridge`, that turns all of this into
native MCP tools:

```bash
cd fluid-mono/packages/mist/mcp && pnpm build
claude mcp add --scope user mist-bridge \
  --env MIST_AGENT_CONTROL_TOKEN="$MIST_AGENT_CONTROL_TOKEN" \
  -- node /Volumes/Code/Fluid/fluid-mono/packages/mist/mcp/dist/bridge-cli.mjs
```

Tools arrive as `mcp__mist-bridge__<mist name>` (names kept verbatim so mist-skills
markdown stays portable), plus `mist_bridge_status` / `mist_bridge_poll` /
`mist_bridge_abort`. Proxy env: `MIST_AGENT_CONTROL_URL` (default
`http://127.0.0.1:9846`), `MIST_AGENT_CONTROL_TOKEN` (required),
`MIST_BRIDGE_TOOL_TIMEOUT_MS` (default `900000`), and `MIST_BRIDGE_PROJECT_PATH` /
`MIST_BRIDGE_COMPANY`, which fill `projectPath` / `companySlug` on every call without the
model seeing them.

With Mist down the proxy does not exit: it serves only `mist_bridge_status`, re-probes on
every `tools/list` and every tool call, and emits `tools/list_changed` when Mist comes
back. Every failure — host down, 401, refusal, the tool's own error — is an `isError`
content result, never a JSON-RPC error.

### Bridge caveats

- **In-memory records.** A Mist restart drops every invocation record. Work that already
  landed is not lost (mutations still have Time Machine entries), but an `invocationId`
  from before the restart is gone.
- **8 concurrent invocations**, separate from the 20-turn cap.
- **No chat.** `projectInfo.chatId` is deliberately omitted, so `run_workflow`'s progress
  card has no chat to link back to and `human_in_the_loop` returns a `pending` payload
  that no Mist bubble renders — the external caller *is* the human.
- **Prompt-injection reach.** A user-scope registration puts production-write tools in
  every Claude Code session, including ones reading untrusted pages. Keep
  `MIST_BRIDGE_ALLOW_WRITES` off for everyday use and pin
  `MIST_BRIDGE_ALLOWED_COMPANIES` to sandbox companies.

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
- **Turn "succeeded" but you don't believe it, or a card should have rendered** →
  screenshot the window instead of guessing. The `cua-driver` skill captures the
  Mist window *and* its Electron DevTools (Network/console) in ~0.2s, in the
  background, without stealing focus:

  ```bash
  cua-driver list_windows '{"pid":<MIST_PID>}' \
    | jq -r '.windows[] | select(.title|test("Fluid Mist|Developer Tools"))
             | "\(.window_id)\t\(.title)\ton_screen=\(.is_on_screen)"'
  cua-driver get_window_state '{"pid":<MIST_PID>,"window_id":<ID>}' \
    --screenshot-out-file /tmp/mist-evidence.png
  ```

  Two constraints: always pass `--screenshot-out-file` (inline base64 is ~165 KB
  of context per snapshot), and **assert `on_screen=true`** — an off-Space window
  returns a frozen frame (byte-identical over 10 minutes when measured) with no
  staleness signal. Capture only: screenshot HITL/consent cards, never click
  them. A bridge-originated proposal is *meant* to need a human.

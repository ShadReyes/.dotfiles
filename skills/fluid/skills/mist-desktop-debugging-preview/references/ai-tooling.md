# AI tooling interpretation

Use this reference to interpret AI-related evidence without turning the Mist skill into a
Vercel AI SDK implementation guide.

## Establish the actual dependency context

Never infer behavior from a remembered AI SDK version. Locate the relevant `package.json` and
lockfile, then record the installed package names and resolved versions. Commonly relevant
packages can include `ai`, `@ai-sdk/openai`, `@ai-sdk/gateway`, `@ai-sdk/mcp`, and other
`@ai-sdk/*` providers.

```bash
jq -r '(.dependencies // {}) + (.devDependencies // {}) |
  to_entries[] | select(.key == "ai" or (.key | startswith("@ai-sdk/"))) |
  [.key, .value] | @tsv' <package.json>
```

If package semantics are central to the diagnosis, consult the documentation or source for the
resolved version. Keep that deeper implementation work outside this skill.

## Interpret the persisted lifecycle

Mist chat artifacts currently express a small lifecycle vocabulary:

- message `role` and `ts` establish speaker and chronology;
- a `text` block records textual output;
- a `tool_use` block can associate `toolName`, `toolUseId`, `input`, and `result`;
- chat and history identifiers can correlate AI activity with workflow or domain actions.

Treat this as Mist's persisted representation. Do not equate its block names or shapes with an AI
SDK's in-memory message or stream-part types.

The observed persisted message shape does not guarantee an explicit finish reason or
stream-termination marker. A complete-looking text block proves that text was persisted, not that
the transport closed normally.

## Useful failure patterns

Test these as hypotheses:

- a tool-use block exists but has no corresponding result or intended side effect;
- the same tool-use identifier appears unexpectedly more than once;
- a message ends during a tool lifecycle or after partial text;
- the chat index timestamp does not reflect the newest persisted message;
- a history action exists without the expected chat correlation, or vice versa;
- a provider or SDK error appears in a result while the surrounding chat still persisted;
- persisted evidence is complete, suggesting a rendering or session-rehydration problem.

Do not label a chat "truncated" solely because a final assistant message is absent. Interruption,
cancellation, tool failure, persistence failure, and an intentionally unfinished workflow can
look similar.

## Structural checks

Summarize block counts without exposing content:

```bash
jq '[.messages[].blocks[]?.type] | group_by(.) |
  map({type: .[0], count: length})' <chat.json>
```

Find duplicate tool-use identifiers:

```bash
jq '[.messages[].blocks[]? | select(.type == "tool_use") | .toolUseId] |
  group_by(.) | map(select(length > 1) | {id: .[0], count: length})' <chat.json>
```

List tool lifecycle metadata:

```bash
jq -r '.messages[] as $message | $message.blocks[]? |
  select(.type == "tool_use") |
  [$message.ts, $message.role, .toolUseId, .toolName, (.result | type)] | @tsv' <chat.json>
```

Only inspect `input`, `result`, or message text after a structural check identifies the relevant
block. Redact secrets and customer data from any report.

## Escalation boundary

Escalate beyond this skill when the evidence requires:

- explaining version-specific AI SDK APIs or stream protocols;
- changing model, provider, gateway, or MCP integration code;
- tracing application source architecture;
- reproducing a provider-side failure.

Carry forward the package versions, minimal failing artifact shape, chronology, and correlation
IDs so the deeper investigation starts from evidence rather than rediscovery.

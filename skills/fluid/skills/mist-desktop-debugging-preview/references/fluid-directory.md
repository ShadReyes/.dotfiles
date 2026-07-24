# Fluid directory evidence map

Use `/Users/shadrac/Fluid` as a runtime data root, not as the Mist Desktop source tree. Its
contents can evolve, so enumerate the current filesystem before relying on this map.

## Working workspaces

Directories such as `/Users/shadrac/Fluid/<workspace>/` contain user-visible Fluid working data.
A workspace may contain:

- `brand.md` and `memory.md`;
- `mysites/` with site content and configuration;
- `themes/` with theme working files;
- `skills/` with skill-related material;
- `skills/.chats/<domain>__<workflow>/` with workflow-specific chat surfaces and outputs;
- `.history/` with an index plus date-partitioned mutation records.

Do not assume every workspace contains every category.

## Harness-managed workspace surfaces

`/Users/shadrac/Fluid/.workspace/<Workspace>/` contains harness-managed surfaces. A surface can
contain `.mist-desktop/` directly or beneath a nested working area such as `time-machine/` or
`skills-library/`.

`.workspace/_unknown/` can contain artifacts that were not associated with a resolved workspace.
Include it when a session appears missing from the expected workspace.

Additional `.mist-desktop/` directories can occur within working subdirectories, including
mysites and workflow chat directories. Never search only the top-level `.workspace` tree.

## Chat artifacts

Each `.mist-desktop/chats/` directory can contain:

- `index.json`: an object with `version`, `nextSeq`, and `chats`; chat entries include `id`,
  `title`, `createdAt`, and `lastActiveAt`;
- `chat-<uuid>.json`: an object with `messages`; messages include `id`, `role`, `ts`, and
  `blocks`;
- text blocks and tool-use blocks; tool-use blocks can include `toolUseId`, `toolName`, `input`,
  and `result`.

Treat these fields as observed local schemas, not permanent contracts.

Useful discovery commands:

```bash
fluid_root=/Users/shadrac/Fluid
find "$fluid_root" -path '*/.mist-desktop/chats/index.json' -type f -print
find "$fluid_root" -path '*/.mist-desktop/chats/chat-*.json' -type f -print
find "$fluid_root" -path '*/skills/.chats/*' -type d -print
```

## History artifacts

`<workspace>/.history/index.json` contains `rows` describing recorded actions. Observed
correlation fields include `id`, `timestamp`, `chatTurnId`, `workflowId`, `companyId`,
`projectId`, `actor`, `method`, `path`, `summary`, and `reversible`.

Dated history JSON files can additionally contain request/response information, before/after
state, and an inverse request. These files may contain customer or operational data. Query only
the keys required for the investigation.

Useful structural queries:

```bash
jq '{version, rowCount:(.rows | length)}' <history-index.json>
jq -r '.rows[] | [.timestamp, .chatTurnId, .workflowId, .id] | @tsv' <history-index.json>
```

## Attachments and generated outputs

`.mist-desktop/attachments/` can hold downloaded media plus `.info.json` metadata. Metadata can
contain source URLs, HTTP headers, or cookies. Do not print or quote it wholesale.

Workflow directories can also contain generated reports or other outputs adjacent to their
`.mist-desktop` data. Use timestamps and chat/history identifiers to establish provenance; file
proximity alone is not proof.

List metadata safely:

```bash
find /Users/shadrac/Fluid -path '*/.mist-desktop/attachments/*' -type f -print
jq 'keys' <attachment.info.json>
```

## Search discipline

- Use `find` for path discovery, `rg -l` for locating textual matches, `jq` for JSON structure,
  and `stat` for filesystem chronology.
- Use fixed-string search (`rg -F`) for UUIDs, titles, and exact error fragments.
- Restrict searches with `--glob` to avoid scanning media, theme repositories, and unrelated
  generated files.
- Preserve paths exactly; directories may differ in case or contain hidden segments.
- Search indexes before payloads, IDs before prose, and narrow paths before the entire root.

Runtime logs are not a guaranteed artifact category under this root. Discover candidates instead
of assuming a location:

```bash
find /Users/shadrac/Fluid -type f \( -name '*.log' -o -name '*.jsonl' \) -print
```

If none correlate with the incident, report that `/Users/shadrac/Fluid` cannot answer the runtime
portion of the diagnosis and request the relevant application log source.

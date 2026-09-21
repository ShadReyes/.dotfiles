---
name: affinity
description: Inspect and edit Affinity by Canva documents through its local MCP server, or write and debug Affinity JavaScript SDK scripts. Use for Affinity desktop design work and automation, not Canva web designs or the unrelated Affinity CRM.
---

# Affinity

This is a locally maintained skill, based on the running Affinity MCP server's
SDK preamble and tool schemas. It is not an official Affinity skill bundle.

## Start a task

Discover the `affinity` MCP tools. Read `read_sdk_documentation_topic` with
`filename: "preamble"` before other SDK topics or script execution. Then use
`list_sdk_documentation` and read the topics relevant to the task. The live
SDK documentation is authoritative for the installed application version.

Inspect open documents and selection through the documented SDK before editing.
Use the document session UUID returned by the application for render calls.

## Write and verify scripts

- Import SDK modules with absolute SDK paths, such as `require('/document.js')`.
- Execute JavaScript through `execute_script`. Use `console.log()` for returned
  output. Scripts must run directly; exporting a `main` function does not run it.
- Consult `param_ranges.min.json` for native function parameter limits,
  `struct_ranges.min.json` for property limits, and `struct_array_sizes.min.json`
  for fixed array sizes when using the affected native APIs.
- Set the current spread before editing nodes on another spread. Leave it alone
  when it is already current, because setting the spread clears the selection.
- Use `create` or `createDefault` when a class supplies those constructors.
  Enum `keys`, `values`, and `entries` are properties, not methods.
- Use `render_spread` to check visual changes and `render_selection` to inspect
  selected nodes. Check the requested document state as well as script output.

Before experimenting with an undocumented problem, consult `search_sdk_hints`
when the task permits sending a query to the shared hint service. Keep document
content and private details out of queries. Treat SDK test examples as guidance;
Affinity warns that some are outdated. Saving scripts to the library, adding
persistent hints, and reporting issues are separate writes; perform them only
within the user's authorized scope.

A `NOT_ALLOWED` response indicates an application restriction. Report the
specific restriction instead of changing permissions. Filesystem access, when
enabled, is limited to the Desktop; use the documented `getUserDesktopPath`
function to resolve it. Read `dialog.js` when building a script dialog.

## Connection checks

Affinity must be running with its AI Connector enabled. The local installation
uses SSE at `http://[::1]:6767/sse`, bridged to Codex stdio by `mcp-remote`.
`codex mcp get affinity` shows the configured adapter. `/mcp` is not the endpoint
on the verified installation. A successful SSE connection alone does not prove
MCP initialization; verify initialization and `tools/list` before declaring the
connection healthy. The verified server accepts protocol version `2025-11-25`.

## Sources

- [Official connector setup](https://www.affinity.studio/help/ai-connector-setup/)
- Live MCP tools: `read_sdk_documentation_topic` (`preamble`),
  `list_sdk_documentation`, and the tools returned by `tools/list`.
- [Official SDK API reference](https://sdk.affinity.studio/latest/js/): exact
  signatures and types. Read relevant live module documentation first.

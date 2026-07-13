---
name: linear-create
description: Create and decompose Fluid Linear Project work on the Current team, with optional parent issues and blocking relations.
user-invocable: true
---

# Fluid Linear Work Creator

Create issues for an identified Linear Project on the `Current` team. Projects
are the primary planning container. Parent/child issue hierarchy is optional;
use it when a workstream benefits from a summary issue and task children.

## Project selection

Before creating issues:

1. Identify the Project from the conversation.
2. If no Project is identified, ask the user to choose one from Current-team
   Projects.
3. If the user requests a new Project, create it with `Current` as its team and
   `Admin & Dev Ex` as its Initiative unless another Initiative is explicitly
   requested.
4. Never infer an Initiative from the assignee. Initiatives describe company
   groups; they do not define issue ownership.

Use the direct GraphQL launcher from `linear-fluid` for all Linear operations.
Resolve names to IDs with the bundled operations before mutations.

## Issue defaults

Every created issue uses:

| Field | Default |
| --- | --- |
| Team | `Current` |
| State | `Todo` |
| Project | The selected Project |
| Priority | Ask when material; otherwise Normal |
| Assignee | Ask when ownership is known; otherwise unset |

Set `parentId` only when using optional issue hierarchy. Do not create a
special container issue merely to imitate a Project.

## Creation flow

1. Gather the desired outcome, Project, ownership, priority, and any known
   dependencies.
2. Resolve the Project and Current team IDs.
3. If a new Project was requested, create it under `Admin & Dev Ex` by default
   and record its ID.
4. Propose the issue breakdown before creating anything. Include titles,
   descriptions, optional parent relationships, and blocking order.
5. Get explicit approval for the proposed breakdown.
6. Create blocking issues first, then create dependent issues with
   `blocks`/`blockedBy` relations.
7. Apply `ready-for-agent` only when the user explicitly approves it for a
   specific issue. Keep it off by default.
8. For every `ready-for-agent` issue, add a durable implementation brief
   comment containing the summary, current behavior, desired behavior,
   acceptance criteria, pointers, and out-of-scope items.
9. Run `linear-triage` for the Project and confirm the dependency graph and
   status-based work order.

## Description guidance

Project summary issues should explain the problem, intended outcome, success
criteria, and scope boundaries. Technical child issues should explain the
affected behavior, implementation constraints, and testable acceptance
criteria.

Implementation briefs must describe behavior and contracts rather than stale
file paths or line numbers. Do not add a brief when the issue is too vague to
have concrete acceptance criteria; ask the user to clarify it first.

## Hard rules

1. Use team `Current` for every issue.
2. Attach every issue to the selected Project.
3. Default newly created Projects to the `Admin & Dev Ex` Initiative.
4. Use Project membership instead of legacy parent-container conventions.
5. Keep `ready-for-agent` opt-in and limited to actionable issues.
6. Preserve blocking relations; they are the source of work-order sequencing.
7. Present the proposed breakdown before any mutation.
8. Verify every mutation with `linear-triage`.

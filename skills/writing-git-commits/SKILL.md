---
name: writing-git-commits
description: Use when creating git commits, writing commit messages, or when commit messages are rejected for being unclear, too long, or poorly formatted
---

# Writing Git Commits

## Overview

Good commit messages matter. They enable efficient collaboration, code archaeology, and understanding of why changes were made. A well-crafted commit history is the difference between `git log` being useful or useless.

**Core principle:** A commit message should complete the sentence "If applied, this commit will [your subject line]."

## The Seven Rules

### 1. Separate subject from body with a blank line

```
Subject line here

Body starts after blank line.
```

Not every commit needs a body—simple changes can be subject-only. But when context is needed, the blank line is critical for `git log`, `git shortlog`, and many Git tools.

### 2. Limit subject line to 50 characters

- 50 characters is the target
- 72 characters is the hard maximum (GitHub truncates beyond this)
- Forces you to think about the most concise way to explain what changed

### 3. Capitalize the subject line

```
# Good
Accelerate to 88 miles per hour

# Bad
accelerate to 88 miles per hour
```

### 4. Do not end the subject line with a period

```
# Good
Open the pod bay doors

# Bad
Open the pod bay doors.
```

Trailing punctuation wastes precious characters and adds no value.

### 5. Use imperative mood in the subject line

Write as if giving a command:

```
# Good (imperative)
Refactor subsystem X for readability
Update getting started documentation
Remove deprecated methods
Release version 1.0.0

# Bad (not imperative)
Fixed bug with Y
Changing behavior of X
More fixes for broken stuff
Sweet new API methods
```

**The test:** Your subject should complete "If applied, this commit will..."
- ✅ "If applied, this commit will **refactor subsystem X for readability**"
- ❌ "If applied, this commit will **fixed bug with Y**"

### 6. Wrap body at 72 characters

Git never wraps text automatically. Wrap manually at 72 characters to allow room for indentation while staying under 80 total.

### 7. Use the body to explain what and why, not how

The code shows the how. The commit message explains:
- **Why** was this change necessary?
- **What** problem does it solve?
- **What** side effects or consequences does it have?

```
commit eb0b56b19017ab5c16c745e6da39c53126924ed6
Author: Pieter Wuille <pieter.wuille@gmail.com>
Date:   Fri Aug 1 22:57:55 2014 +0200

    Simplify serialize.h's exception handling

    Remove the 'state' and 'exceptmask' from serialize.h's stream
    implementations, as well as related methods.

    As exceptmask always included 'failbit', and setstate was always
    called with bits = failbit, all it did was immediately raise an
    exception. Get rid of those variables, and replace the setstate
    with direct exception throwing (which also removes some dead
    code).

    As a result, good() is never reached after a failure (there are
    no longer528 non-exception-throwing failures), and can just be
    replaced by !eof().

    fail(), currentar(), and in_avail() are just removed as they
    are never used.
```

## Quick Reference

| Rule | Do | Don't |
|------|-----|-------|
| Subject length | ≤50 chars (72 max) | Long rambling subjects |
| Subject case | `Add feature` | `add feature` |
| Subject punctuation | `Fix the bug` | `Fix the bug.` |
| Subject mood | `Add`, `Fix`, `Remove` | `Added`, `Fixed`, `Removing` |
| Body wrap | 72 characters | Unwrapped paragraphs |
| Body content | Why and what | How (code shows that) |

## Common Mistakes

**"Fixed stuff"** - Vague subjects that don't describe what changed. Be specific: "Fix null pointer in user authentication"

**Past tense subjects** - "Added feature" instead of "Add feature". Use imperative mood.

**No context in body** - Just restating what the diff shows. Explain *why* the change was needed.

**Mixing concerns** - One commit doing multiple unrelated things. Each commit should be one logical change.

## Format Template

```
<type>: <subject max 50 chars, imperative mood, no period>

<body wrapped at 72 chars explaining why, not how>

<footer with issue refs, breaking changes, co-authors>
```

Example:
```
Fix user authentication timeout on slow networks

The previous 5-second timeout was too aggressive for users on
high-latency connections, causing frequent authentication failures
in regions with poor connectivity.

Increase timeout to 30 seconds and add exponential backoff for
retries. This matches the behavior of our mobile clients.

Resolves: #1234
Co-Authored-By: Claude <noreply@anthropic.com>
```

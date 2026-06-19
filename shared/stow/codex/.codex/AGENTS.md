# Global Instructions

## Rules

- Never include AI attribution, signatures, or self-identification in code comments or commit messages.

## Devcontainer

The Rails backend (`fluid`) runs inside a Docker devcontainer. All Rails/Ruby/bundle/rake commands must go through `docker exec`.

## PR Summaries

When creating pull requests:

1. **What changed** - Brief description of the changes
2. **Why it changed** - Context and motivation
3. **How to test** - Steps to verify the changes
4. **Linear** - Link to the Linear issue

Extract the Linear URL from the branch name or issue lookup.

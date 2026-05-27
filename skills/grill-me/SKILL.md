---
name: grill-me
description: Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me". Triggers on design review requests, plan interrogation, or decision validation.
---

# Grill Me

## Overview

Interview the user relentlessly about every aspect of their plan or design until reaching shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

## Process

1. **Identify the plan or design** - Read any referenced documents, issues, or code. If the user hasn't stated the plan, ask for it.

2. **Map the decision tree** - Identify every major decision, assumption, and dependency in the plan. Group them into branches.

3. **Walk each branch depth-first** - For each decision point:
   - State the decision clearly
   - Provide your recommended answer with reasoning
   - If the question can be answered by exploring the codebase, explore the codebase instead of asking
   - Wait for the user to confirm, reject, or modify before moving on
   - If a decision depends on an unresolved earlier decision, flag the dependency and resolve that first

4. **Challenge assumptions** - For each branch:
   - What could go wrong?
   - What are the alternatives you considered?
   - What are you optimizing for and what are you trading off?
   - Are there hidden dependencies or ordering constraints?

5. **Converge** - Once all branches are resolved, summarize the final shared understanding as a concise decision log.

## Rules

- One question at a time. Do not dump a list of 10 questions.
- Provide your recommended answer for each question so the user can simply agree or push back.
- Be relentless. Do not stop because the user seems confident. Dig deeper.
- If a question can be answered by reading code, reading docs, or exploring the repo, do that yourself instead of asking.
- Track resolved vs unresolved decisions. Show progress.
- When all branches are resolved, produce a final summary.

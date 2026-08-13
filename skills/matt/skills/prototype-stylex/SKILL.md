---
name: prototype-stylex
description: Build throwaway UI prototypes as radically different variants authored with StyleX. Use when the user explicitly asks to explore what an interface should look like with StyleX, compare a StyleX prototype track with the host styling system, or evaluate StyleX while prototyping UI.
---

# StyleX UI Prototype

Use the sibling prototype skill's UI workflow, with StyleX as the deliberate styling constraint.

## Inherit the base workflow

Before acting, read [the base prototype skill](../prototype/SKILL.md) and its [UI branch](../prototype/UI.md) completely. Follow both except where this skill overrides them.

Apply this skill only to UI questions. If the question is about logic, state transitions, or data shape, use the base prototype's logic branch without StyleX.

## Override the styling system

- Author all prototype-owned styles with `@stylexjs/stylex`, including the floating variant switcher.
- Import StyleX as `import * as stylex from '@stylexjs/stylex'`. Define styles with `stylex.create()` and apply them with `stylex.props()`.
- Co-locate each variant's styles with that variant. Give style keys semantic names that explain their role.
- Keep variants structurally independent. Do not introduce a shared layout abstraction that makes them converge.
- Reuse compatible host components and tokens when useful, but do not convert unrelated application code to StyleX.
- Keep existing global resets and necessary host styles. Do not add Tailwind utilities, CSS modules, styled components, or new handwritten classes for prototype-owned styling.
- Use inline styles only for values that are genuinely computed at runtime. Do not use them to bypass StyleX's static constraints.
- Introduce `defineVars`, `createTheme`, recipes, or shared primitives only when the question needs them. A prototype is not an excuse to build a design system.

## Choose the integration shape

Inspect the framework, bundler, package manager, and existing StyleX configuration before editing.

- If StyleX is already configured, reuse it and prefer the base skill's existing-page sub-shape.
- If it is not configured, consult the current official StyleX installation guide for the detected framework and add the smallest compatible runtime and build-time setup.
- Preserve the existing build pipeline. If StyleX would require a broad compiler migration or destabilize the host app, isolate the experiment in a clearly named adjacent prototype harness and record that the missing real-app shell weakens the comparison.
- Keep the prototype runnable through one existing task-runner command.

Treat StyleX setup as prototype infrastructure: limit it to what makes the experiment run, and remove it from main with the losing prototype code unless the StyleX track itself is adopted.

## Capture two answers

When the prototype is judged, record both decisions:

1. Which UI variant won, and why.
2. Whether StyleX helped enough to adopt, considering setup cost, iteration speed, component readability, interoperability with the host app, and cleanup cost.

Do not infer that choosing a UI variant also approves StyleX. Capture the two verdicts separately, then follow the base skill's branch-capture and cleanup rules.

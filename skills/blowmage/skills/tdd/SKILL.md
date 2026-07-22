---
name: tdd
description: >-
  Classicist (Detroit-school) test-DRIVEN development that drives and defends software design with tests — not merely test-first.
  Use when implementing any feature, bugfix, or refactor, or whenever writing or strengthening tests.
  Produces a cheat-proof test suite that reads as a specification, with edge and malformed inputs explicitly decided (never accidental crashes), and design pain answered by decomposition.
  Real collaborators; doubles only at external boundaries.
  Triggers: "TDD", "test-driven", "write tests", "add tests", "test this", "drive this with tests", designing code with tests, making a test suite defensible, hardening code against edge cases, or fixing a bug.
---

# Test-Driven Design (tdd)

## The distinction that matters

**Test-first is about ordering.**
**Test-driven is about the design being driven and defended by tests.**
Writing the test first is a means; it is not the goal.
The goal is four properties of what you produce:

1. A suite so strong a lazy hack cannot pass it. (defensible)
2. Every edge and malformed input explicitly *decided*, never accidental. (decided)
3. A design that changed when the tests told you it was wrong. (design feedback)
4. A suite that reads as the specification of the design. (spec)

If you wrote tests first but produced none of these, you did test-first, not test-driven.
This skill exists to produce these results in a single pass, by **attacking your own work with things you actually run** — because reasoning about whether your tests are good is unreliable, but *running* a cheat against them is not.

## Stance: classicist

This skill is **classicist** (Detroit / bottom-up): tests exercise **real collaborators** and assert **observable behavior and state**; test doubles stand in only for boundaries you do not own.
The outside-in / mockist school — driving design by mocking collaborators and asserting their interactions — is a different discipline and is out of scope here.
If you want it, pair a separate BDD skill with this one; do not blend the two.

## The loop

For each behavior, smallest first:

1. **Intend.**
   Write the smallest test that expresses the next behavior.
   If it is genuinely new behavior, run it and watch it FAIL — *fail*, not *error*, and for the reason you intend (the behavior is missing), not a typo or an import error.
   Make it pass with the simplest code that works — no speculative generality.
   Then run the WHOLE suite: all green, output pristine (no warnings), no regressions.
2. **Attack (grounded — the heart of this skill).**
   Do not move on.
   Run the two attacks against what you just wrote (see "The grounded attack").
3. **Listen.**
   If writing that test hurt — heavy setup, or you can feel the case count multiplying — the design is fighting you.
   Decompose before continuing (see "Listen to the tests").
4. Repeat until the behavior is fully specified and every attack comes up empty.
5. **Standardize.**
   Refactor code and tests under green into a readable spec (see "Standardize into a spec").
6. **Accept.**
   Run the acceptance checklist before you claim done.

Work one slice at a time: one test → make it pass → attack → next.
Do NOT write a batch of tests up front and then implement against them.
Tests written in bulk verify *imagined* behavior and lock you into a structure before you understand the code; each test should respond to what the last cycle taught you.
Let the first slice be a tracer bullet — pick one that proves the whole path end to end, then widen.

Steps 2 and 3 are the ones everyone skips.
They are not optional here.

## Do not rationalize past the attack

The grounded attack (Steps 2–3) *is* the skill; everything else is scaffolding around it.
You will want to skip it — the code looks obviously right, the function is trivial, you are in a hurry.
That wanting is the signal, not the exception.
The moment you start building an argument for why *this* case does not need the cheat run or the edge battery, stop: the argument is the rationalization, and writing it costs more than running the check would.
The check is cheap and mechanical; your belief that the tests are good is neither — so run the check, do not trust the belief.
Doing the test-first motions without the attack is not this skill; it is test-first theater.
The letter is the spirit: if you skipped the attack, you did not do this — no matter how the diff looks.

For one behavior driven all the way through the loop and both attacks, see [references/worked-example.md](references/worked-example.md).

## The grounded attack (AC1 + AC2)

After a test is green, become the adversary.
The adversary does not *think*; it *runs*.

### Attack 1 — can a cheat survive? (defensible suite)

Replace the implementation with a deliberate cheat and RUN the suite.
If the suite still passes, it is too weak — add the test that kills the cheat, then restore.

```ruby
# real code
def compare_release(a, b) = KEY.(a) <=> KEY.(b)

# CHEAT: hardcode the last case you added. Run the suite.
def compare_release(a, b) = -1
```

```console
$ ruby solution_test.rb
# If this is GREEN, your suite is a lie. A constant passed it.
# Add a case that forces a real answer, then put the real code back.
```

Cheats to try, in order: return a constant; `if a == "<the exact tested input>"`; handle only the happy path; ignore an argument.
Save the hardest for last — the *lenient* cheat: an implementation that is correct on every valid input but silently accepts garbage (returns a plausible answer for malformed input instead of rejecting it).
A suite that only exercises valid inputs cannot tell the lenient cheat from the real thing; killing it is what forces the edge *assertions* of Attack 2, not just edge decisions.
Each surviving cheat is a missing test.
Keep going until every cheat turns the bar red.

This is mutation testing done by hand: your cheat is one *mutant*.
The systematic version flips a single thing in the real code — an operator (`<` → `<=`), a boundary constant, a dropped branch — and reruns the suite; a mutant that survives marks a line that runs but is never truly asserted.
If a mutation-testing tool is available, use it and aim to kill every mutant; if not, mutate by hand at the spots most likely to hide a bug (comparisons, boundaries, off-by-one).

### Attack 2 — what happens at the edges? (decided assumptions)

Enumerate boundary and malformed inputs and actually CALL the code with each.
For every one, you must make an explicit decision — you may not leave it to luck.

```ruby
[nil, "", "foo", 1, "1.2", "1.2.3.4.5", "1.0.0-nightly.x", "  1.0.0  "].each do |x|
  begin
    p [x, compare_release(x, "1.0.0")]
  rescue => e
    p [x, e.class]        # an ACCIDENTAL crash is a bug until you DECIDE it
  end
end
```

For each input, pick one and pin it:

- **Handle** it → add a test for the defined behavior.
- **Reject** it → decide the error and add a test that it raises: `assert_raises(ArgumentError) { compare_release("foo", "1.0.0") }`.
- **Out of scope** → write a one-line note recording the decision (in a comment or a DECISIONS note).
  Do not add speculative handling for it (YAGNI) — but the decision is now explicit, not accidental.

An unhandled `NoMethodError` / `ArgumentError` you did not choose is a defect.
A raised error you *decided on* and *tested* is a feature.
The difference is the whole point of AC2.
Beware the decision you make from ignorance: deciding is mandatory, but a decision that contradicts the domain (e.g. rejecting input a spec says to accept) is still wrong — the skill makes your assumption explicit and testable, it cannot supply knowledge you lack.

When the battery is homogeneous, you may drive it with a table of `(input, expected-decision)` rows instead of copy-pasting tests — but only if the table stays legible: label each row and give it its own failure message so a failure names the offending case, keep one concept per table, and split out any row that is really a different behavior.
A table that hides which case failed, or lumps unrelated behaviors together to look tidy, is worse than the duplication it removed.

## Listen to the tests — decompose (AC3)

A test that is hard to write is telling you the design is wrong.
The signals and the response:

| Signal | Response |
|--------|----------|
| Arrange block must set up several independent things at once, or one new option multiplies the cases | Extract the varying responsibility into its own object; test it directly; give the caller a seam (a collaborator it can be handed). |
| You reach for a double of your OWN code to make a test pass | The design is too coupled. Introduce a seam so the real collaborator can be substituted, or split the responsibility. Doubling your own code is a design smell, not a testing tactic. |
| You must reach into internals or test a private method to assert anything | Drive it through the public interface; if you cannot, the behavior wants to live in its own object with its own public seam. |

Record the decision to decompose (a comment or note).
Guard against over-doing it: add a seam only where an independently varying responsibility actually multiplies the burden — not at every boundary.

When you do decompose, aim for a **deep module** — a small public interface over a substantial implementation — and prefer composition over inheritance.
A unit that is hard to test wants a smaller, deeper public seam, not more layers; the test difficulty is pointing at the interface, not only the internals.

## When you cannot write the test

Stuck on how to test it?
Write the test you WISH you could — invent the ideal API and the assertion you want to make — then make that API real.
The test is a design tool: the shape that is pleasant to call is the shape to build.
If the only way to test it is to reach inside or mock your own code, that is design feedback (see "Listen to the tests"), not a reason to lower the bar.

## Fixing a bug

A bug is a missing test.
Before you touch the fix, write a test that reproduces the bug and watch it FAIL — that proves the test actually catches the bug.
Then fix the code and watch it pass.
Never fix a bug without a failing test first: otherwise you cannot know the fix works, and nothing stops the bug returning.

## Standardize into a spec (AC4)

Once green and the attacks come up empty, make the suite read as a specification — this is real work, not cleanup:

- **One *concept* per test, not one assertion.**
  Multiple assertions that describe facets of the *same* outcome belong together; split when the *scenario* changes, merge when only the assertion changes.
  Use assertion messages to say what each check verifies.
- Intent-revealing names in a consistent scheme.
- Group tests by behavior, in an order that reads as the design's story.
- Add characterization tests for any correct-but-untested decision (a branch that happens to be right but that no test pins).
- Remove a test only if removing it lowers confidence in nothing.

```ruby
class CompareReleaseTest < Minitest::Test
  # --- ordering by version number ---
  def test_lower_version_is_older
    assert_equal(-1, compare_release("1.4.0", "1.5.0"))
  end

  # --- malformed input is rejected (decided: reject, see DECISIONS) ---
  def test_non_version_string_is_rejected
    assert_raises(ArgumentError) { compare_release("foo", "1.0.0") }
  end
end
```

## Arrange-Act-Assert, and test data

Each test has three visible parts: **Arrange** (build the world), **Act** (one call to the behavior under test), **Assert** (check the observable result).
Keep the Arrange **explicit in the test body** — hidden setup (shared `setup`/`before` hooks, instance variables carried between tests) makes a test impossible to read on its own.
See [Arrange-Act-Assert](https://wiki.c2.com/?ArrangeActAssert).

When a test must arrange rich, stateful objects — entities with several independent attributes, not pure functions whose inputs are just values — build test data from a **small set of named archetypes and mutate them per test**, never a bespoke record per case.
A record-per-case explodes multiplicatively (5 dimensions × 4 values ≈ hundreds of records) and rots; a few archetypes plus one-line mutations scale additively.
Name data by role/story, not by number (`suspended_account`, not `user_2`); default each archetype to the happy path and put the edge case one mutation away.
This is the combinatorial trap again (see AC3); detail in [references/classicist-testing.md](references/classicist-testing.md).

## Test doubles — the classicist rule

Use **real collaborators** and assert **observable behavior/state**.
Double ONLY boundaries you do not own: the network/HTTP, the filesystem, the clock, randomness, third-party services.
NEVER double the unit under test, an internal collaborator, or your own models/services — reaching for one is design feedback (introduce a seam at the boundary), not a testing tactic.
Every double carries a one-line comment naming the boundary it stands in for.
For the classicist anti-patterns (don't assert on the double, no test-only methods in production, over-mocking, incomplete doubles, testing through the seam and its side effects), read [references/classicist-testing.md](references/classicist-testing.md) when you add a double.

## Red flags — STOP, you are doing test-first, not test-driven

- You reached green and moved to the next behavior without running a cheat against the suite.
- You never called the code with `nil`, `""`, or a malformed value.
- A test raised an error you did not decide on and you left it.
- You wrote the whole implementation from memory, then retrofitted tests around its internals.
- You wrote several tests before making any of them pass (a bulk "splurge" instead of one slice at a time).
- You doubled an internal collaborator or the unit under test to make a test pass.
- A test asserts a method was called, or reaches into private state.
- You added generality/config/an abstraction no test forced.
- A single test covers more than one scenario (its name needs "and").
- You are about to claim done without running the acceptance checklist.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "The suite is obviously good, I don't need to run a cheat" | Then a cheat will fail instantly — so run it. If you won't run it, you don't know. |
| "Edge cases are obvious / out of scope" | Then RUN them and write the one-line decision. Undecided is not out-of-scope; it's a latent crash. |
| "It's a simple function, TDD is overkill" | Simple functions ship the accidental `nil` crash. The attack takes two minutes. |
| "I'll harden it later" | Later never runs the garbage inputs. Now does. |
| "I already manually tested it" | Manual testing leaves no record and cannot rerun. The suite is the record. |
| "I'll mock the internal service to isolate it" | Mocking your own code tests the mock and freezes a bad seam. Use the real collaborator; if that's hard, fix the design. |
| "More tests = better" | No. Defensible + decided = better. A vacuous test is noise. |
| "The design is fine, I'll just add another branch" | If the cases are multiplying, the design is fighting you. Decompose. |
| "I'll write all the tests first, then implement" | Bulk tests verify imagined shape and lock the design before you understand it. One slice at a time: test → pass → next. |
| "I can't test everything, so I'll just cover the important paths" | "Can't test everything" is design feedback, not a licence to skip — a test space that explodes is telling you to decompose until you CAN cover it. The gap is the signal. |

## When NOT to use

- Throwaway spikes/exploration — but throw the spike away and drive the real thing.
- Pure config/data files with no behavior.
- Generated code.

Ask the human before skipping on anything with real behavior.

## Acceptance checklist (run before claiming done)

- [ ] **AC1** I ran at least one cheat implementation against the suite and it failed.
- [ ] **AC2** I ran boundary + malformed inputs; each is handled-and-tested, raises-and-tested, or documented out-of-scope.
      No undecided crash remains.
- [ ] **AC3** Where a test fought me, I decomposed (or recorded why not).
- [ ] **AC4** The suite reads top-to-bottom as a spec: one concept per test, clear names, grouped.
- [ ] The full suite is green with pristine output (no warnings), no regressions.
- [ ] Tests use real collaborators and assert behavior, not mechanism; doubles only at external boundaries.
      No speculative code.
      Steps were small.

Cannot check all of AC1–AC4?
You are not done.
Go back to the attack.

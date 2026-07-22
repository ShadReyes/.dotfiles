# Classicist testing — collaborators, doubles, and anti-patterns

Load this when you are about to add a test double, or when a test involves collaborators.
It is the classicist (Detroit-school) detail behind the one-line rule in SKILL.md.

Contents:
- Core principle
- What to double, what never to double
- Test through the seam (behavior + side effects)
- Anti-patterns (with the gate for each)
- One concept per test
- Test data — archetypes (only for stateful/entity-heavy tests)
- Layered testing
- Checklist

## Core principle

Test what the code does, not what a double does.
A double is a means to isolate a boundary; it is never the thing under test.
Prefer the real collaborator.
Reach for a double only when the real thing crosses a boundary you do not own and cannot control in a test.

## What to double, what never to double

**Double only boundaries you do not own:**
- the network / HTTP / third-party APIs
- the filesystem (when the real thing is impractical)
- the clock (`Time.now`, timers) and randomness (seeds, UUIDs)
- external services (payment gateways, mail delivery transport, cloud SDKs)

**Never double:**
- the unit under test
- an internal collaborator, your own models, services, or business logic
- anything whose real behavior the test actually depends on

Reaching for a double of your own code is **design feedback**, not a testing tactic.
It means the seam is in the wrong place: introduce a seam at the boundary, or split the responsibility so the logic can be tested directly through its own public interface.

Every double gets a one-line comment naming the boundary it stands in for:

```ruby
# Double: PaymentGateway (external API — we don't own it)
gateway = Minitest::Mock.new
gateway.expect(:charge, { ok: true }, [Money])
```

## Test through the seam (behavior + side effects)

Test a unit through its **public interface**: inputs in, observable outputs and
side effects out.
Never assert on internals or private methods — drive them through the public seam.

Assert the side effects that matter, **including that they do not happen** when they should not:

```ruby
def test_high_value_order_notifies_finance
  notifier = FakeNotifier.new                          # double: the notification boundary
  PlaceOrder.new(notifier: notifier).call(order: expensive_order)
  assert_equal 1, notifier.sent.size                   # side effect happened
end

def test_low_value_order_does_not_notify_finance
  notifier = FakeNotifier.new
  PlaceOrder.new(notifier: notifier).call(order: cheap_order)
  assert_equal 0, notifier.sent.size                   # side effect did NOT happen
end
```

## Anti-patterns

### 1. Asserting on the double

Verifying the double exists or was called tells you nothing about real behavior.

```ruby
# BAD: asserts the stub, not the behavior
renderer.expect(:call, "<sidebar/>")
assert_equal "<sidebar/>", page.render_sidebar

# GOOD: assert the observable result of the real unit
assert_includes page.render, "role=\"navigation\""
```

Gate: before asserting on anything double-related, ask "am I asserting real behavior, or just that my double was invoked?"
If the latter, delete the assertion or drop the double.

### 2. Test-only methods on production classes

A method that exists only for tests pollutes production and violates YAGNI.

```ruby
# BAD: Session#destroy exists only so tests can clean up
class Session
  def destroy = @workspace&.destroy
end

# GOOD: cleanup lives in a test helper, not the production class
module SessionTestHelper
  def cleanup(session) = session.workspace&.destroy
end
```

Gate: before adding a method to a production class, ask "is this only used by tests?"
If yes, it goes in a test helper.

### 3. Over-mocking (breaking a side effect the test needs)

Mocking a method that had a side effect the test depended on makes the test pass for the wrong reason.

```ruby
# BAD: stubbing the writer the duplicate-check depends on
Catalog.stub(:persist, nil) do
  add(server); add(server)   # should raise "duplicate" — but can't, persist was stubbed
end

# GOOD: double the slow/external part only; keep the behavior the test needs
HttpClient.stub(:get, canned_response) do
  add(server); assert_raises(Duplicate) { add(server) }   # real persistence runs
end
```

Gate: before doubling, ask "what side effects does the real method have, and does this test depend on any of them?"
Double at the lowest boundary; run with the real thing first if you are unsure what the test needs.

### 4. Incomplete doubles

A double that returns only the fields you thought of hides structural assumptions and fails silently when downstream code reads a field you omitted.

Mirror the real contract completely, not just the fields the immediate line uses.

### 5. Doubles more complex than the real thing

If the double's setup is longer than the test, or you are doubling many things to make one test pass, that is the signal to use the real collaborators (an integration-style test) instead.
Complex doubles are a symptom; the cure is fewer doubles, not more.

### 6. Testing private methods / internal state

Drive private behavior through the public interface.
If a private method is complex enough to want its own test, it wants to be its own object with its own public seam.

### 7. Brittle assertions

- No absolute counts (`assert_equal 5, things.count`) — assert the specific change or existence instead.
- Do not assert setup state (that the thing you just created exists); assert the behavior under test.
- Assert specific values, not vague types (`assert_equal "completed", status`, not `assert_kind_of String, status`).

## One concept per test

The goal is one *concept* per test (Kent Beck), not one `assert`.
Assertions that together describe a single coherent outcome are one concept and belong together.
Split when the *scenario* changes; merge when only the *assertion* changes.
Use assertion messages so a multi-assert test is still diagnosable on failure.

## Test data — archetypes, not a record per case

This section applies only when a test must arrange **rich, stateful objects** — entities with several independent attributes, as in data-backed or domain-heavy systems.
It does not apply to pure functions, whose inputs are just values; skip it there.

Build such test data from a small set of **named archetypes** and **mutate them per test**.
A bespoke record per case explodes multiplicatively: 5 independent dimensions with 3–4 values each is 243–1024 combinations, and one record per combination rots into a maintenance vortex.
A handful of archetypes plus one-line mutations scales additively instead.

- **Name by role/story, not by number** — `suspended_account` tells you everything; `user_2` tells you nothing.
- **Default to the happy path** — each archetype is the normal, successful state, and the edge case is one mutation away in the test body (`account.suspend!`), visible right where it matters.
- **Value is how many tests can mutate it**, not how many use it verbatim — a generic `active` archetype dozens of tests can bend beats a `suspended_account_with_declined_card` usable by exactly one.
- **Mutate explicitly and loudly** — so a failed precondition surfaces instead of silently not applying.

Anti-patterns: a record per variation; sequential names (`member_1`, `member_2`); data added "just in case"; a complex graph built for a single test (inline it instead).

## Layered testing

Each layer trusts the layers below and does not re-test them.
Unit tests carry the business-logic coverage (the seam contract: inputs, outputs, side effects).
Higher layers (integration, end-to-end) test contracts and wiring, not every branch a lower layer already covers.
Over-testing a lower layer's concern from a higher layer is duplicated cost, not extra safety.

## Checklist

- [ ] Real collaborators used; doubles only at boundaries I do not own.
- [ ] Every double comments the boundary it stands for.
- [ ] No assertion checks merely that a double was called/exists.
- [ ] No test-only methods added to production code.
- [ ] No private methods or internal state asserted directly.
- [ ] Side effects asserted — including that they do NOT happen when they shouldn't.
- [ ] Specific-value assertions; no absolute counts; no asserting setup state.
- [ ] One concept per test.

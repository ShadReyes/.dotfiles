# Worked example — one behavior, end to end

One small behavior driven through the whole loop, including both attacks, so the
rhythm is concrete.
The task: `initials(full_name)` returns the uppercase initials of a name
(`"Ada Lovelace"` → `"AL"`).
Code is illustrative; the point is the sequence of moves, not the language.

## 1. Intend — smallest test, watch it fail, minimal green

```ruby
def test_initials_of_a_two_word_name
  assert_equal "AL", initials("Ada Lovelace")
end
```

Run it: it fails because `initials` does not exist yet — a genuine RED (missing behavior), not a typo.
Make it pass with the simplest thing:

```ruby
def initials(full_name) = full_name.split.map { |w| w[0] }.join.upcase
```

Run the whole suite: green, output clean.

## 2. Attack 1 — can a cheat survive?

Replace the body with a constant and run the suite:

```ruby
def initials(full_name) = "AL"     # cheat
```

It stays **green** — one example cannot tell a constant from real logic.
The suite is a lie so far.
Add a second, different example to kill the cheat:

```ruby
def test_initials_of_another_two_word_name
  assert_equal "GH", initials("Grace Hopper")
end
```

Now the constant fails.
Restore the real implementation; both pass.
Try the next cheat — `full_name.split.map { |w| w[0] }.join` without `.upcase`?
Add a lowercase case if nothing yet forces the upcasing (see step 3).

## 3. Attack 2 — what happens at the edges?

Run a battery and look at every result:

```ruby
[nil, "", "   ", "Prince", "  Ada   Lovelace ", "josé ferrer", "Jean-Luc Picard"].each do |x|
  begin; p [x, initials(x)]; rescue => e; p [x, e.class]; end
end
```

What comes back, and the decision for each:

| Input | Raw result | Decision |
|-------|-----------|----------|
| `nil` | `NoMethodError` (accidental) | **Reject** — non-String / blank is a caller error → `ArgumentError`. |
| `""`, `"   "` | `""` (silent, useless) | **Reject** — a blank name has no initials → `ArgumentError`. |
| `"Prince"` | `"P"` | **Handle** — a single name yields a single initial. Pin it. |
| `"  Ada   Lovelace "` | `"AL"` | **Handle** — surrounding/among-word whitespace collapses. Pin it so it can't regress. |
| `"josé ferrer"` | `"JF"` | **Handle** — result is upcased (this is what forces `.upcase`). Pin it. |
| `"Jean-Luc Picard"` | `"JP"` | **Decide** — only whitespace separates words, so a hyphenated name is one word. Document the choice; pin `"JP"`. |

Encode each decision as a test (reject cases with `assert_raises(ArgumentError)`), and update the code to honor the rejections:

```ruby
def initials(full_name)
  raise ArgumentError, "name must be a non-blank String" unless full_name.is_a?(String) && !full_name.strip.empty?

  full_name.split.map { |word| word[0] }.join.upcase
end
```

Re-run the battery: no accidental crash remains; every input is either a defined result or a deliberate, tested `ArgumentError`.

## 4. Listen — is the design fighting me?

No.
It is a single pure function with a linear pipeline (split → first char → join → upcase); no test needed heavy setup, and no responsibility multiplied into independent dimensions.
Record "no decomposition warranted" and move on — do not invent a seam the tests never demanded.

## 5. Standardize — the suite reads as a spec

Group by behavior, one concept per test, intent-revealing names:

```ruby
class InitialsTest < Minitest::Test
  # --- basic initials ---
  def test_two_word_name_gives_two_initials
    assert_equal "AL", initials("Ada Lovelace")
    assert_equal "GH", initials("Grace Hopper")   # same concept: kills a hardcoded constant
  end

  def test_single_name_gives_one_initial
    assert_equal "P", initials("Prince")
  end

  # --- normalization ---
  def test_surrounding_and_inner_whitespace_is_ignored
    assert_equal "AL", initials("  Ada   Lovelace ")
  end

  def test_initials_are_uppercased
    assert_equal "JF", initials("josé ferrer")
  end

  # --- word boundaries: whitespace only (decided; see comment) ---
  def test_hyphenated_name_counts_as_one_word
    assert_equal "JP", initials("Jean-Luc Picard")
  end

  # --- a blank or non-string name is rejected ---
  def test_blank_name_is_rejected
    assert_raises(ArgumentError) { initials("   ") }
  end

  def test_nil_is_rejected
    assert_raises(ArgumentError) { initials(nil) }
  end
end
```

## 6. Accept

Walk the acceptance checklist: a cheat was run and killed (AC1); every edge is
decided and tested, no undecided crash (AC2); the "no decomposition" call is
recorded (AC3); the suite reads top-to-bottom as a spec (AC4); the full suite is
green and pristine.
Done — and the tests now *describe* what a valid name is and how initials are
formed, edges and refusals included.

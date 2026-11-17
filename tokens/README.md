# tokens

The design tokens: colours, the type scale, spacing, radii and badge sizes. The spec is the guidelines, from [*Colours are written in OKLCH*](../guidelines/brand-guidelines.md#colours-are-written-in-oklch) to [*Spacing*](../guidelines/brand-guidelines.md#spacing-a-4-px-grid).

- `tokens.json`: every token value, versioned; written by `palette.py`, never edited by hand.
- `palette.py`: the palette's rules and the type scale; writes `tokens.json`, and `--check` verifies it and every contrast pair.
- `to_oklch.py`: writes each colour as OKLCH from its sRGB hex; `--check` verifies every value round-trips.
- `LICENSE`: MIT, for this folder: the tokens and the scripts.

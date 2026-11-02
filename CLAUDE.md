# suveryn-brand

The sūveryn mark, fonts, design tokens and brand guidelines. Licences differ per part: the logo is all rights reserved ([TRADEMARK_POLICY.md](TRADEMARK_POLICY.md)), the tokens are MIT (so the AGPL core and anyone else can copy them), the fonts are each under their own OFL, the guidelines are CC BY 4.0.

Start with [guidelines/brand-guidelines.md](guidelines/brand-guidelines.md). For what sūveryn is, the private [suveryn-handbook](https://github.com/suveryn/suveryn-handbook).

## Rules

- **`tokens/tokens.json` is written, never edited.** `tokens/palette.py` holds the palette's rules (OKLCH, one neutral hue, even lightness steps, hover and ink as fixed offsets) and the type scale (fourteen named styles); run it to regenerate, `--check` verifies every value and every contrast pair. CI fails if the file is stale.
- **Every text colour passes 4.5:1**, measured from OKLCH lightness. Never white text on the accent orange or teal: use `on-accent`.
- **A new size or colour is added to the brand first**, with its rule, then used in a product. Core's chat UI and the appliance's theme copy this repository at a pinned commit and fail tests on a drift or a literal.
- **Two themes differ on purpose**: dark is the brand and marketing identity; light is the product UI.
- **Version the tokens** (`v3.4` at 28 October 2026) and say in the guidelines what each colour means. A consumer re-syncs by moving its pin; a token change is not finished until the consumers' pins can move without breaking their tests.
- **One branch and PR per change.** Merge only when Filip says so.
- **Copy** in the guidelines: UK English, "sūveryn" lower case except at a sentence start or as the company, no em dashes. IBM Plex Mono is for the wordmark only.

## Verify

```bash
python tokens/palette.py --check && git diff --exit-code tokens/tokens.json
```

# Sūveryn

AI for work that can't leave the premises.

## What sūveryn is

Sūveryn is an open-source, on-premise AI platform for organisations that handle confidential data: legal, healthcare, government, financial services. It runs entirely on infrastructure the customer chooses, works fully offline or air-gapped, and never sends documents to the cloud. Sūveryn Labs does not sell hardware — certified partners size, install and support it.

Two editions: **Sūveryn Open** (free, self-hosted, AGPL core) and **Sūveryn Enterprise** (certified builds, premium connectors, SLAs, sold through certified partners).

## Naming

Sūveryn is a phonetic respelling of "sovereign," reflecting the platform's core idea: sovereignty over your own data, on your own premises, under your own control. The macron over the u marks the long vowel sound.

## Positioning

Lead with the benefit, not the architecture. The proposition is **"AI for work that can't leave the premises,"** not "an on-premise, open-source, air-gapped AI platform." On-premise, open source and air-gap capability are the reasons the benefit is credible — they support the pitch, they aren't the pitch itself.

## Tone of voice

Confident, precise, technically credible, understated. Sober rather than hyped — the visual direction (below) is explicitly inspired by enterprise security vendors like Palo Alto Networks, not by consumer AI marketing. Avoid generic AI-hype language ("revolutionary," "game-changing"); avoid over-explaining architecture before stating the benefit.

Always write **"premises,"** plural. "Premise" (singular) means an assumption in English, and the tagline depends on the correct word.

## Wording and spelling

- **Tagline:** "AI for work that can't leave the premises." This exact wording everywhere it appears: the website headline and page title, social images, the web manifest, documentation and repository descriptions. No "Private" in front. "Private AI" is fine as a plain descriptor inside a sentence; it is not part of the tagline.
- **UK English throughout:** organisation, summarise, analyse, colour, grey, licence (the noun; `license` is the verb). Proper names keep their published spelling, such as "Business Source License" and "SIL Open Font License", and so does code, such as the CSS property `color`.
- **The name:** "sūveryn", lowercase and with the macron. A capital S is used in only three cases: at the start of a sentence; in the company name, "Sūveryn Labs" (formally "Sūveryn Labs Ltd"); and in product names, such as "Sūveryn Open" and "Sūveryn Enterprise". Everywhere else, mid-sentence and in headings included, it is written "sūveryn": "Build your own sūveryn appliance", "Is sūveryn open source?". The wordmark is always lowercase, "sūveryn", set in IBM Plex Mono. Plain "suveryn" appears only where a macron cannot: web addresses, repository and file names, email addresses and identifiers.
  - **Where the name opens a label or a string, it keeps the capital S.** Examples: page titles ("Sūveryn setup · Welcome"), the installer bar ("Sūveryn installer"), email subjects ("Sūveryn: email test"), package descriptions ("Sūveryn engine: …") and the alternative name in the website's search data. The name is the first word in each, so it counts as the start of a sentence. The chat interface's test in suveryn-core checks the same rule.
  - **"Sūveryn Design System" keeps its capital S**, as a name, like "Sūveryn Labs".
- **Edition names:** "Sūveryn Open" and "Sūveryn Enterprise". Never "Community" or "Commercial" as edition names.
- **Terms:** "on-premise" as the adjective (an on-premise platform); "open source" as a noun and "open-source" as an adjective; "air-gapped" as the adjective and "air-gap capable"; "premises" always plural.
- **Legal entity:** "Sūveryn Labs Ltd" in formal text.

## Visual identity: two themes, not one

Sūveryn runs two genuinely different surfaces, and the token system is built around that split rather than papering over it:

- **Dark** is the brand's primary identity — the marketing site, the enterprise-security visual language, the one most people will first see.
- **Light** is the actual product UI. Chat interfaces are something people read for long stretches; a fully dark app was tested directly against a light one and the light interface won, on readability grounds, independent of brand preference. The product deliberately does not force the marketing site's dark theme onto the thing people work in every day.

Both themes share the same token names and the same accent colours — only the neutrals (bg, surface, the text levels) and the contrast-sensitive aliases (`accent-hover`, `accent-ink`, `teal-ink`) change value between them; `on-accent` is `ink` in both. See `tokens.json` for the exact values; every text colour is checked by OKLCH computation (see *Measuring contrast* below), not assumed by eye.

## Colours are written in OKLCH

Since tokens v3 every colour in `tokens.json` is an `oklch()` value (and since v3.1 every value comes from the rules in `tokens/palette.py`, see *The palette's rules* below) (CSS Color 4): lightness 0 to 1, chroma, hue in degrees, and an alpha after `/` for the translucent ones. That is what goes into CSS as it is; browsers have drawn OKLCH since 2023 (Chrome 111, Safari 15.4, Firefox 113), so no fallback is written. Beside each value, `srgb` holds the same colour as sRGB hex (with its alpha), for tools that can't read OKLCH and for anyone used to the old values; it is derived, never the source. The two are kept equal by `tokens/to_oklch.py --check`.

Why OKLCH: it is the space the contrast rule already reasons in. A hover state, a dimmer text level or a wash is now a change of lightness or alpha on the same hue, visibly even across the orange, the teal and the neutrals, and a future dark theme or a new accent is made the same way. Derived colours in product CSS (a wash of the teal, a shadow of the ink) are written as `oklch()` on the token's own lightness, chroma and hue with an alpha, never as a new hex.

## The one hard contrast rule

**Never put white text on the accent orange or on teal.** Measured the way this system measures contrast (below), white-on-accent is 2.91:1 and white-on-teal 1.93:1 — both fail WCAG AA. Every button, chip and badge in this system uses `on-accent` (an alias to `ink`, the same dark neutral in both themes) for text and icons sitting on an accent-filled surface. This is not a stylistic preference; it's a measured fix for a real contrast failure, and it should not be relitigated per-component.

## Measuring contrast

Contrast is measured from OKLCH lightness: a colour's luminance is taken as L³ (L being its OKLCH/OKLab lightness), and the WCAG ratio (Y₁ + 0.05) / (Y₂ + 0.05) is applied. Translucent colours (the text levels, `line`, washes) are blended onto the surface they sit on first. Thresholds are WCAG AA: **4.5:1 for text**, 3:1 for large text and for UI components such as switch tracks and focus borders.

When a colour fails as text, the fix keeps its hue and lowers (light theme) or raises (dark theme) its OKLCH lightness until every surface it's used on passes, reducing chroma only where sRGB can't show it. That is how the `-ink` tokens are made: `teal-ink` from `teal`, `accent-ink` from `accent`. So **use `accent-ink`, not `accent`, for orange text such as links**; `accent` stays for fills, the mark and active states.

Verified pairs (worst case over bg, surface and surface-alt), by this measure and by WCAG's own sRGB formula (the smaller of the two; `tokens/palette.py` prints both for every pair):

| Token | Light | Dark |
|---|---|---|
| `text` | 18.2:1 | 12.8:1 |
| `text-dim` | 5.8:1 | 6.5:1 |
| `text-dimmer` | 4.5:1 | 4.5:1 |
| `accent-ink` | 4.7:1 | 4.8:1 |
| `teal-ink` (incl. on the 10% teal wash) | 4.6:1 | 7.3:1 |
| `on-accent` on `accent` / `accent-hover` | 6.5:1 / 5.1:1 | 6.5:1 / 7.8:1 |
| `control-off` (UI, 3:1) on surface-overlay, dark bg, light bg | ≥ 3.9:1 | ≥ 3.4:1 |
| `focus` (UI, 3:1) on bg, surface, surface-alt | ≥ 3.7:1 | ≥ 7.3:1 |

## The palette's rules (tokens v3.1)

Since v3.1 no colour in `tokens.json` is picked by hand: `tokens/palette.py` holds the rules and writes every value, and `--check` fails when the file and the rules disagree.

- **One neutral hue.** Every grey, from the ink to the white surfaces, sits on 258°, the hue of the dark surfaces (the brand's identity surface), at a small chroma. Before v3.1 the greys ranged from 245° to 286°, so a dimmed ink next to a control looked like greys from different sets.
- **Even lightness steps per theme.** Light surfaces at L 1.000, 0.980 and 0.955; dark surfaces at 0.160, 0.205 and 0.290; the ink at 0.090, the dark text at 0.967. The dim text levels stay alphas of the text, so they follow whatever surface they sit on.
- **States are lightness offsets on the family's hue.** The accent is L 0.677 at 34.6°; its hover is −0.06 on light surfaces and +0.045 on dark ones; as text (`accent-ink`) it is −0.15 on light surfaces and +0.02 on dark ones. The teal is L 0.790 at 188.4°; as text it is −0.27 on light surfaces, and as a UI boundary (`focus`, since v3.2: the focus ring and the border of a focused field) −0.218, which holds the 3:1 non-text contrast on every light surface. Chroma is the base's, reduced only where sRGB can't show it. A future second accent is made the same way.

Changing a rule changes every colour it governs, consistently; that is the point of writing the palette in OKLCH.

## Where the teal goes (tokens v3.3)

The orange means *act*. The teal means *the system vouches for this*: where an answer comes from and that it was checked. In the product UI it is used for exactly these, and nothing else:

- the assistant's mark;
- citation markers in an answer, and the cited passage marked in the source panel;
- a playbook's coverage ("Gedekt");
- the focus ring and the border of a focused field (`focus`);
- `case-surface`, the background of a conversation inside a case.

People are not the system: avatars are ink initials on `surface-alt` with a `line` border, never teal. Statuses ("ready", "confirmed"), filters, progress bars, the reasoning indicator and chips are ink and neutral surfaces. A colour that marks everything marks nothing.

`case-surface` sits at the surface's lightness (light) or surface-alt's (dark) with a little of the teal's chroma on the teal's hue, so every text colour that holds on those surfaces holds on it too; `tokens/palette.py` checks the pairs. It is a background only: never a fill for controls, never behind a personal conversation.

## Typography

Three families, three distinct jobs, never swapped:

- **Space Grotesk** — headings and display text. Tested directly against IBM Plex Sans (the mono's own sibling family) for full tonal consistency with the wordmark, and deliberately kept: Space Grotesk's rounder, slightly more characterful letterforms read as a touch more approachable than the otherwise serious palette, which was judged a feature, not a drift from the brand.
- **Inter** — all body copy and UI text. The workhorse. Everything that isn't a heading or the wordmark.
- **IBM Plex Mono** — the wordmark, and only the wordmark. Originally JetBrains Mono; switched to IBM Plex Mono for slightly more open spacing at small sizes. Using this font anywhere else (labels, body copy, code blocks) is a brand violation, not a style choice.

### The type scale (tokens v3.2)

Every text style a surface may use is named in `tokens.json` (`type.groups`), written by `tokens/palette.py` from `TYPE_SCALE`, and checked by `--check`. A surface uses these and nothing else: no size that isn't on this list. Before v3.2 the brand named seven styles, and the chat UI, the appliance's setup page, the login page and the website each filled the gaps on their own (eighteen sizes in the chat UI, fourteen on the site, buttons at a size the brand didn't name on all three); these fourteen are the styles those surfaces turned out to need, named once.

| Style | Family | Size | Line height | Weight | Used for |
|---|---|---|---|---|---|
| `h1` | Space Grotesk | 48px | 1.1 | 600 | Hero and page headlines (the site scales it with `clamp(34px, 5.4vw, 54px)`) |
| `h2` | Space Grotesk | 28px | 1.2 | 600 | Section headings |
| `title` | Space Grotesk | 22px | 1.2 | 600 | Page and dialog titles in the product, the setup and login titles, edition cards, a key figure |
| `subtitle` | Space Grotesk | 18px | 1.3 | 600 | Card and step titles that need more than h3, FAQ questions |
| `h3` | Space Grotesk | 15px | 1.3 | 600 | Small card titles, conversation titles, component labels |
| `body` | Inter | 15px | 1.6 | 400 | Running text, the composer, fields |
| `control` | Inter | 14.5px | 1.2 | 600 | Buttons, tabs, navigation links, the titles of rows and options |
| `ui` | Inter | 14.5px | 1.4 | 400 | Compact UI text at the control's size: status rows, the login page's fields |
| `body-sm` | Inter | 13.5px | 1.55 | 400 | Chat messages, card copy, dialog text, notices, small buttons |
| `ui-sm` | Inter | 13px | 1.5 | 400 | Hints and errors, table cells, menu items, the access log |
| `caption` | Inter | 12px | 1.5 | 400 | Fine print, timestamps, metadata, chart legends and axes |
| `label` | Inter | 11px | 1.3 | 600, uppercase, 0.04em | Section labels, eyebrows, the citation marker |
| `wordmark` | IBM Plex Mono | 22px | 1 | 500 | The wordmark at header scale |
| `wordmark-lg` | IBM Plex Mono | 32px | 1 | 500 | The wordmark as a hero, on the setup page only |

In CSS the styles are variables generated from the tokens (`--text-body`, `--text-ui-sm`, and so on, each a size, with the line height and weight beside it), so a stylesheet says which style a thing has rather than how many pixels it is. Weight and colour may vary within a style (a `body-sm` at 600 is a small emphasised line; `caption` in `text-dim` is the usual metadata); size and family may not.

## Iconography

**Lucide** (ISC licence, MIT-compatible; the subset of icons derived from Feather is MIT) is the icon library for all UI chrome — navigation, buttons, status indicators. This was decided after a separate design-system export surfaced "Untitled UI" as the apparent icon set in use, which turned out to be a paid, commercially licensed kit with no confirmed rights to reuse outside its original project. What was actually doing the visual work in that export was Lucide, used as a free stand-in because it shares Untitled UI's stroke style — so Lucide became the real, permanently-adopted choice rather than chasing a licence sūveryn never had. Both licences are permissive but require the copyright and permission notice to travel with copies, so keep Lucide's licence text with any distributed copy of the icons (the site and the chat visual embed several as inline SVG).

The brand mark itself (below) is not from Lucide and is never swapped for a generic icon.

## The brand mark

A rounded square containing a short horizontal bar above a small square — read as a roof over a room, over the premises. Delivered as real asset files, not re-derived:

- [`logo/suveryn-icon.svg`](../logo/suveryn-icon.svg) — the full icon, single-ink orange
- [`logo/suveryn-logotype-dark-bg.svg`](../logo/suveryn-logotype-dark-bg.svg) — icon + wordmark lockup, for dark surfaces
- [`logo/suveryn-logotype-light-bg.svg`](../logo/suveryn-logotype-light-bg.svg) — icon + wordmark lockup, for light surfaces
- [`logo/favicon.svg`](../logo/favicon.svg) — the icon tuned for browser-tab sizes (16 to 48px)
- [`logo/apple-touch-icon.png`](../logo/apple-touch-icon.png) — the icon in orange on an opaque white tile, 180px, for iPhone and Android home screens
- [`logo/icon-192.png`](../logo/icon-192.png), [`logo/icon-512.png`](../logo/icon-512.png) — the same, 192 and 512px, for a web app manifest (also as maskable icons: the mark stays inside the safe zone)
- [`logo/suveryn-github-avatar.png`](../logo/suveryn-github-avatar.png) — the icon on a dark tile, 512px, for the GitHub organisation

The favicon and app icons use the same shapes with strokes about 20% heavier, so the bar and the box stay readable at 16px. That optical adjustment is the only permitted change to the mark; never redraw it.

App icons are orange on white, like the favicon on a light page: Google Search and other places that show a site's icon may pick the largest one offered, so every icon a site offers shows the mark the same way. The dark tile is kept only for the GitHub avatar.

Nav/header usage: 30px icon, 22px wordmark, 12px gap between them — this exact ratio is the live site's own header and should be matched wherever the lockup appears at a comparable scale, not re-proportioned per instance.

## A named interaction pattern: no assistant bubble

The chat interface deliberately does not give the assistant's reply a message bubble — only the user's turn gets one. This is the interface's most recognisable trait, chosen because it reads as a considered answer sitting on the page rather than a chat-widget reply in a box. The chat interface in [suveryn-core](https://github.com/suveryn/suveryn-core) implements both halves (`UserMessage` and `AssistantMessage` in `packages/chat-ui`); they are not interchangeable, and giving the assistant a bubble "for symmetry" undoes the reason this pattern was chosen.

File attachments belong with the message that introduces them (the user's turn), not retrofitted onto the reply as a citation — a citation and an attachment are different things and should not share one visual treatment.

## Further reading

The full reasoning behind every decision summarised here — the naming history, the competitive landscape, the commercial model, the open items — lives in the Sūveryn Strategic Plan document, not duplicated here. This README documents the system as built; that document explains why.

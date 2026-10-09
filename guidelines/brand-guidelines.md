# Sūveryn

AI for work that can't leave the premises.

## What Sūveryn is

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
- **The name:** "Sūveryn", with the macron, in all running text. The wordmark is always lowercase, "sūveryn", set in IBM Plex Mono. Plain "suveryn" appears only where a macron cannot: web addresses, repository and file names, email addresses and identifiers.
- **Edition names:** "Sūveryn Open" and "Sūveryn Enterprise". Never "Community" or "Commercial" as edition names.
- **Terms:** "on-premise" as the adjective (an on-premise platform); "open source" as a noun and "open-source" as an adjective; "air-gapped" as the adjective and "air-gap capable"; "premises" always plural.
- **Legal entity:** "Sūveryn Labs Ltd" in formal text.

## Visual identity: two themes, not one

Sūveryn runs two genuinely different surfaces, and the token system is built around that split rather than papering over it:

- **Dark** is the brand's primary identity — the marketing site, the enterprise-security visual language, the one most people will first see.
- **Light** is the actual product UI. Chat interfaces are something people read for long stretches; a fully dark app was tested directly against a light one and the light interface won, on readability grounds, independent of brand preference. The product deliberately does not force the marketing site's dark theme onto the thing people work in every day.

Both themes share the same token names and the same accent colours — only the neutrals (bg, surface, text) and the two contrast-sensitive aliases (`on-accent`, `teal-ink`) actually change value between them. See `tokens.json` for the exact values; every colour was checked by direct OKLCH computation, not assumed by eye.

## The one hard contrast rule

**Never put white text on the accent orange or on teal.** This system's own colour audit measured white-on-accent at 2.88:1 and white-on-teal at 1.66:1 — both fail WCAG AA. Every button, chip and badge in this system uses `on-accent` (an alias to `ink`, the same dark neutral in both themes) for text and icons sitting on an accent-filled surface. This is not a stylistic preference; it's a measured fix for a real contrast failure, and it should not be relitigated per-component.

## Typography

Three families, three distinct jobs, never swapped:

- **Space Grotesk** — headings and display text. Tested directly against IBM Plex Sans (the mono's own sibling family) for full tonal consistency with the wordmark, and deliberately kept: Space Grotesk's rounder, slightly more characterful letterforms read as a touch more approachable than the otherwise serious palette, which was judged a feature, not a drift from the brand.
- **Inter** — all body copy and UI text. The workhorse. Everything that isn't a heading or the wordmark.
- **IBM Plex Mono** — the wordmark, and only the wordmark. Originally JetBrains Mono; switched to IBM Plex Mono for slightly more open spacing at small sizes. Using this font anywhere else (labels, body copy, code blocks) is a brand violation, not a style choice.

## Iconography

**Lucide** (ISC licence, MIT-compatible; the subset of icons derived from Feather is MIT) is the icon library for all UI chrome — navigation, buttons, status indicators. This was decided after a separate design-system export surfaced "Untitled UI" as the apparent icon set in use, which turned out to be a paid, commercially licensed kit with no confirmed rights to reuse outside its original project. What was actually doing the visual work in that export was Lucide, used as a free stand-in because it shares Untitled UI's stroke style — so Lucide became the real, permanently-adopted choice rather than chasing a licence Sūveryn never had. Both licences are permissive but require the copyright and permission notice to travel with copies, so keep Lucide's licence text with any distributed copy of the icons (the site and the chat visual embed several as inline SVG).

The brand mark itself (below) is not from Lucide and is never swapped for a generic icon.

## The brand mark

A rounded square containing a short horizontal bar above a small square — read as a roof over a room, over the premises. Delivered as real asset files, not re-derived:

- [`logo/suveryn-icon.svg`](../logo/suveryn-icon.svg) — the full icon, single-ink orange
- [`logo/suveryn-logotype-dark-bg.svg`](../logo/suveryn-logotype-dark-bg.svg) — icon + wordmark lockup, for dark surfaces
- [`logo/suveryn-logotype-light-bg.svg`](../logo/suveryn-logotype-light-bg.svg) — icon + wordmark lockup, for light surfaces
- [`logo/favicon.svg`](../logo/favicon.svg) — the icon tuned for browser-tab sizes (16 to 48px)
- [`logo/apple-touch-icon.png`](../logo/apple-touch-icon.png) — the icon on an opaque dark tile, for iPhone and Android home screens
- [`logo/suveryn-github-avatar.png`](../logo/suveryn-github-avatar.png) — the icon on a dark tile, 512px, for the GitHub organisation

The favicon and app icons use the same shapes with strokes about 20% heavier, so the bar and the box stay readable at 16px. That optical adjustment is the only permitted change to the mark; never redraw it.

Nav/header usage: 30px icon, 22px wordmark, 12px gap between them — this exact ratio is the live site's own header and should be matched wherever the lockup appears at a comparable scale, not re-proportioned per instance.

## A named interaction pattern: no assistant bubble

The chat interface deliberately does not give the assistant's reply a message bubble — only the user's turn gets one. This is the single most recognisable trait carried over from genuine Claude-style chat interfaces, adopted specifically because it reads as a considered answer sitting on the page rather than a chat-widget reply in a box. The chat interface in [suveryn-core](https://github.com/suveryn/suveryn-core) implements both halves (`UserMessage` and `AssistantMessage` in `packages/chat-ui`); they are not interchangeable, and giving the assistant a bubble "for symmetry" undoes the reason this pattern was chosen.

File attachments belong with the message that introduces them (the user's turn), not retrofitted onto the reply as a citation — a citation and an attachment are different things and should not share one visual treatment.

## Further reading

The full reasoning behind every decision summarised here — the naming history, the competitive landscape, the commercial model, the open items — lives in the Sūveryn Strategic Plan document, not duplicated here. This README documents the system as built; that document explains why.

# Fonts

All three families are Google Fonts, licensed under the SIL Open Font
License 1.1 (see each family's `OFL.txt`). Sourced from the official
[google/fonts](https://github.com/google/fonts) repository.

| Family | File | Used for |
|---|---|---|
| Space Grotesk | `SpaceGrotesk/SpaceGrotesk-Variable.woff2` (variable, wght 300-700) | Display/heading text (weights 500/600/700 per tokens.json) |
| Inter | `Inter/Inter-Variable.woff2` (variable, wght+opsz) | Body/UI text (weights 400/500/600/700 per tokens.json) |
| IBM Plex Mono | `IBMPlexMono/IBMPlexMono-Medium.woff2` (static, weight 500) | The wordmark only — never body copy or UI labels |

`.woff2` is the web-ready compressed format; the matching `.ttf` is kept
alongside for design tools or non-web use. Variable fonts cover every
weight tokens.json references in one file via the `wght` axis.

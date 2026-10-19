"""The palette and the type scale as rules (tokens v3.2): one neutral hue, even lightness steps,
hover, ink and boundary states as fixed lightness offsets on the family's hue; and the text styles
every surface may use, each a name with a size, line height and weight. Writes the ``value`` and
``srgb`` of every colour token and the ``type.groups`` styles in tokens/tokens.json from these
rules, and reports the contrast of the pairs the guidelines verify. Run from the repository root:

    python3 tokens/palette.py            write tokens.json and print the contrast table
    python3 tokens/palette.py --check    exit 1 if tokens.json differs from the rules, or a pair fails

Contrast is measured two ways: the Design System's (luminance = OKLCH L³, see the guidelines,
"Measuring contrast") and WCAG's own sRGB formula. Both must pass.
"""

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = HERE / "tokens.json"

# ---------------------------------------------------------------- the rules
NEUTRAL_HUE = 258.0      # the dark surfaces' hue, the brand's identity surface; every grey sits on it
ACCENT_HUE = 34.6        # the orange
TEAL_HUE = 188.4         # the teal

# (lightness, chroma) per neutral, light and dark theme. Light surfaces step 1.000, 0.980, 0.955;
# dark surfaces 0.160, 0.205, 0.290: even steps within each theme.
NEUTRALS = {
    "bg":              {"light": (1.000, 0.000), "dark": (0.160, 0.010)},
    "surface":         {"light": (0.980, 0.002), "dark": (0.290, 0.014)},
    "surface-alt":     {"light": (0.955, 0.004), "dark": (0.205, 0.012)},
    "text":            {"light": (0.090, 0.014), "dark": (0.967, 0.002)},
    "ink":             {"light": (0.090, 0.014), "dark": (0.090, 0.014)},
    "surface-overlay": {"light": (0.235, 0.013), "dark": (0.235, 0.013)},
    "control-off":     {"light": (0.588, 0.016), "dark": (0.588, 0.016)},
}
# Translucent neutrals: the text (light) or bg (dark) hue with an alpha, as before.
ALPHAS = {
    "line":        {"light": ("text", 0.12), "dark": ("text", 0.12)},
    "text-dim":    {"light": ("text", 0.62), "dark": ("text", 0.66)},
    "text-dimmer": {"light": ("text", 0.55), "dark": ("text", 0.51)},
}
# The accent and the teal: a base, and states as lightness offsets on the same hue. Chroma is the
# base's, reduced only where sRGB can't show it.
ACCENT = (0.677, 0.201)
TEAL = (0.790, 0.125)
HOVER_LIGHT, HOVER_DARK = -0.060, +0.045   # darker on light surfaces, lighter on dark ones
INK_OFFSET = {"accent": -0.150, "teal": -0.270}  # as text on light surfaces: holds 4.5:1 on every surface, both measures
INK_DARK_OFFSET = {"accent": +0.020}                 # as text on dark surfaces: the accent itself is 4.44:1 on surface by WCAG
INK_CHROMA = {"accent": 0.191, "teal": 0.093}    # sRGB can't show the full chroma at that lightness
# The teal as a UI boundary (the focus ring, the border of a focused field): 3:1 on every light
# surface. On dark surfaces the teal itself holds it.
BOUNDARY_OFFSET = {"teal": -0.218}
BOUNDARY_CHROMA = {"teal": 0.097}
# The case surface (tokens v3.3): the background of a conversation inside a case, so the person sees
# they are working in a case and not in a personal conversation. A neutral surface's lightness with a
# little of the teal's chroma on the teal's hue: light at the surface's 0.980, dark at surface-alt's
# 0.205, so every text pair that holds on those holds here too (checked below).
CASE_SURFACE = {"light": (0.980, 0.014), "dark": (0.205, 0.014)}

# ---------------------------------------------------------------- the type scale (v3.2)
# Every text style a surface may use: (group, size px, line height, weight, extras). Before v3.2
# the brand named seven styles and the chat UI, the setup page, the login page and the website
# each filled the gaps on their own (eighteen sizes in the chat UI, fourteen on the site); these
# are the styles those surfaces turned out to need, named once. A surface uses these and nothing else.
TYPE_SCALE = {
    "h1":          ("Display", "48px", "1.1", 600, {}),
    "h2":          ("Display", "28px", "1.2", 600, {}),
    "title":       ("Display", "22px", "1.2", 600, {}),
    "subtitle":    ("Display", "18px", "1.3", 600, {}),
    "h3":          ("Display", "15px", "1.3", 600, {}),
    "body":        ("Body", "15px", "1.6", 400, {}),
    "control":     ("Body", "14.5px", "1.2", 600, {}),
    "ui":          ("Body", "14.5px", "1.4", 400, {}),
    "body-sm":     ("Body", "13.5px", "1.55", 400, {}),
    "ui-sm":       ("Body", "13px", "1.5", 400, {}),
    "caption":     ("Body", "12px", "1.5", 400, {}),
    "label":       ("Body", "11px", "1.3", 600, {"letterSpacing": "0.04em"}),
    "wordmark":    ("Wordmark", "22px", "1", 500, {}),
    "wordmark-lg": ("Wordmark", "32px", "1", 500, {}),
}
TYPE_USAGE = {
    "h1": "Hero and page headlines. Scales with clamp(34px, 5.4vw, 54px) on the live site; 48px is the desktop reference size.",
    "h2": "Section headings, on the site and in the product (an empty case's name, the sign-in page's title at full width).",
    "title": "Page and dialog titles in the product (Administration, Usage, a dialog's heading), the setup page's title, the login page's title, the edition cards' names, a key figure in a totals row.",
    "subtitle": "Card and step titles that need more than h3: the site's how-it-works steps and callout values, the FAQ questions.",
    "h3": "Small card titles, chat and conversation titles, component labels.",
    "body": "Default running text: paragraphs on the site, the composer, a field's text, an empty state's introduction.",
    "control": "Buttons, tab buttons, navigation links, the titles of rows, cards and options: the text of something you act on.",
    "ui": "Compact UI text at the control's size without its weight: status rows, the login page's fields, nav links.",
    "body-sm": "Secondary body text: chat messages, card copy, dialog text, notices, small buttons and inputs, a tab in the product.",
    "ui-sm": "Dense secondary UI text: hints and errors under a field, table cells, menu items and select buttons, the access log, chart tables.",
    "caption": "Fine print, disclaimers, timestamps, metadata under a title, chart legends and axes, text buttons in a list.",
    "label": "Section labels and eyebrow text, set in uppercase in use; also the citation marker in an answer.",
    "wordmark": "The sūveryn wordmark at header scale, next to a 30px mark with a 12px gap. IBM Plex Mono is reserved for this one use: never body copy, never UI labels (originally JetBrains Mono; switched for slightly more open spacing at small sizes).",
    "wordmark-lg": "The wordmark as a hero, on the appliance's setup page (26px below 480px). Never elsewhere.",
}

# ---------------------------------------------------------------- OKLab (Björn Ottosson), sRGB
def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gamma(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def to_linear_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def in_gamut(L, C, H) -> bool:
    return all(-1e-6 <= c <= 1 + 1e-6 for c in to_linear_rgb(L, C, H))


def fit_chroma(L, C, H) -> float:
    """The largest chroma up to C that sRGB shows at this lightness and hue."""
    if in_gamut(L, C, H):
        return C
    lo, hi = 0.0, C
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if in_gamut(L, mid, H) else (lo, mid)
    return lo


def srgb(L, C, H):
    return tuple(min(1.0, max(0.0, _gamma(min(1.0, max(0.0, c))))) for c in to_linear_rgb(L, C, H))


def hex_of(rgb): return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def oklch_of_rgb(rgb):
    r, g, b = (_lin(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


# ---------------------------------------------------------------- the palette
def colour(L, C, H, alpha=None):
    C = round(fit_chroma(L, C, H), 4)
    value = f"oklch({L:.4f} {C:.4f} {H:.2f})" if alpha is None else f"oklch({L:.4f} {C:.4f} {H:.2f} / {alpha:g})"
    hexed = hex_of(srgb(L, C, H))
    return {"value": value, "srgb": hexed if alpha is None else f"{hexed} / {alpha:g}", "L": L, "C": C, "H": H, "alpha": alpha}


def palette() -> dict[str, dict[str, dict]]:
    """token name -> theme -> colour (or an alias, as {"alias": name})."""
    p: dict[str, dict] = {}
    for name, themes in NEUTRALS.items():
        p[name] = {t: colour(L, C, NEUTRAL_HUE) for t, (L, C) in themes.items()}
    for name, themes in ALPHAS.items():
        p[name] = {}
        for t, (base, a) in themes.items():
            b = p[base][t]
            p[name][t] = colour(b["L"], b["C"], b["H"], a)
    aL, aC = ACCENT
    p["accent"] = {t: colour(aL, aC, ACCENT_HUE) for t in ("light", "dark")}
    p["accent-hover"] = {"light": colour(aL + HOVER_LIGHT, aC, ACCENT_HUE), "dark": colour(aL + HOVER_DARK, aC, ACCENT_HUE)}
    p["accent-ink"] = {"light": colour(aL + INK_OFFSET["accent"], INK_CHROMA["accent"], ACCENT_HUE),
                       "dark": colour(aL + INK_DARK_OFFSET["accent"], aC, ACCENT_HUE)}
    p["on-accent"] = {t: {"alias": "ink"} for t in ("light", "dark")}
    tL, tC = TEAL
    p["teal"] = {t: colour(tL, tC, TEAL_HUE) for t in ("light", "dark")}
    p["teal-ink"] = {"light": colour(tL + INK_OFFSET["teal"], INK_CHROMA["teal"], TEAL_HUE), "dark": colour(tL, tC, TEAL_HUE)}
    p["focus"] = {"light": colour(tL + BOUNDARY_OFFSET["teal"], BOUNDARY_CHROMA["teal"], TEAL_HUE), "dark": colour(tL, tC, TEAL_HUE)}
    p["case-surface"] = {t: colour(L, C, TEAL_HUE) for t, (L, C) in CASE_SURFACE.items()}
    return p


def type_groups(existing: list[dict]) -> list[dict]:
    """``type.groups`` from TYPE_SCALE, keeping the family each group names in the file."""
    families = {g["name"]: g["family"] for g in existing}
    groups: dict[str, list] = {}
    for name, (group, size, lh, weight, extra) in TYPE_SCALE.items():
        style = {"name": name, "fontSize": size, "lineHeight": lh, "fontWeight": weight, **extra, "usage": TYPE_USAGE[name]}
        groups.setdefault(group, []).append(style)
    return [{"name": g, "family": families.get(g, g.lower()), "styles": styles} for g, styles in groups.items()]


# ---------------------------------------------------------------- contrast, both ways
def blend(c, over):
    """Opaque sRGB of a colour with an alpha over an opaque one."""
    a = c["alpha"] if c["alpha"] is not None else 1.0
    fg, bg = srgb(c["L"], c["C"], c["H"]), srgb(over["L"], over["C"], over["H"])
    return tuple(a * f + (1 - a) * b for f, b in zip(fg, bg))


def ratio_wcag(fg_rgb, bg_rgb) -> float:
    y = [0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b) for r, g, b in (fg_rgb, bg_rgb)]
    hi, lo = max(y), min(y)
    return (hi + 0.05) / (lo + 0.05)


def ratio_oklch(fg_rgb, bg_rgb) -> float:
    """The Design System's measure: luminance as OKLCH lightness cubed."""
    y = [oklch_of_rgb(c)[0] ** 3 for c in (fg_rgb, bg_rgb)]
    hi, lo = max(y), min(y)
    return (hi + 0.05) / (lo + 0.05)


# (foreground, background, needed) per theme; "wash" is the teal at 10 % over bg (the badge).
PAIRS = [
    ("text", "bg", 4.5), ("text", "surface", 4.5), ("text", "surface-alt", 4.5),
    ("text-dim", "bg", 4.5), ("text-dim", "surface", 4.5), ("text-dim", "surface-alt", 4.5),
    ("text-dimmer", "bg", 4.5), ("text-dimmer", "surface", 4.5), ("text-dimmer", "surface-alt", 4.5),
    ("accent-ink", "bg", 4.5), ("accent-ink", "surface", 4.5), ("accent-ink", "surface-alt", 4.5),
    ("teal-ink", "bg", 4.5), ("teal-ink", "surface", 4.5), ("teal-ink", "surface-alt", 4.5), ("teal-ink", "wash", 4.5),
    ("ink", "accent", 4.5), ("ink", "accent-hover", 4.5), ("ink", "teal", 4.5),
    ("control-off", "surface-overlay", 3.0), ("control-off", "bg", 3.0), ("control-off", "surface", 3.0),
    ("focus", "bg", 3.0), ("focus", "surface", 3.0), ("focus", "surface-alt", 3.0),
    ("text", "case-surface", 4.5), ("text-dim", "case-surface", 4.5), ("text-dimmer", "case-surface", 4.5),
    ("accent-ink", "case-surface", 4.5), ("teal-ink", "case-surface", 4.5), ("focus", "case-surface", 3.0),
]


def contrast_table(p):
    rows = []
    for theme in ("light", "dark"):
        for fg, bg, need in PAIRS:
            f = p[fg][theme]
            if bg == "wash":
                teal = p["teal"][theme]
                bg_rgb = blend({**teal, "alpha": 0.10}, p["bg"][theme])
            else:
                b = p[bg][theme]
                bg_rgb = blend(b, p["bg"][theme])
            fg_rgb = blend(f, {"L": oklch_of_rgb(bg_rgb)[0], "C": oklch_of_rgb(bg_rgb)[1], "H": oklch_of_rgb(bg_rgb)[2]})
            rows.append((theme, fg, bg, need, ratio_oklch(fg_rgb, bg_rgb), ratio_wcag(fg_rgb, bg_rgb)))
    return rows


def main() -> None:
    data = json.loads(TOKENS.read_text())
    p = palette()
    check = "--check" in sys.argv
    problems = []
    for token in data["color"]["tokens"]:
        if token["name"] not in p:
            problems.append(f"{token['name']}: no rule")
            continue
        for theme in ("light", "dark"):
            c = p[token["name"]][theme]
            want_value = f"{{{c['alias']}}}" if "alias" in c else c["value"]
            if check:
                if token["value"][theme] != want_value:
                    problems.append(f"{token['name']} ({theme}): {token['value'][theme]} is not the rule's {want_value}")
            else:
                token["value"][theme] = want_value
                if "alias" not in c:
                    token.setdefault("srgb", {})[theme] = c["srgb"]
                elif "srgb" in token:
                    del token["srgb"]
    want_groups = type_groups(data["type"]["groups"])
    if check:
        have = {s["name"]: {k: v for k, v in s.items() if k != "usage"} for g in data["type"]["groups"] for s in g["styles"]}
        want = {s["name"]: {k: v for k, v in s.items() if k != "usage"} for g in want_groups for s in g["styles"]}
        for name in sorted(set(have) | set(want)):
            if have.get(name) != want.get(name):
                problems.append(f"type style {name}: {have.get(name)} is not the rule's {want.get(name)}")
    else:
        data["type"]["groups"] = want_groups
        if "focus" not in {t["name"] for t in data["color"]["tokens"]}:
            data["color"]["tokens"].append({"name": "focus", "value": {}, "usage": (
                "Focus rings and the border of a focused field: the teal as a UI boundary. Darkened on light "
                "surfaces so it holds the 3:1 non-text contrast on bg, surface and surface-alt (the teal's "
                "lightness minus 0.218, tokens v3.2); the teal itself on dark surfaces. Was a literal in the "
                "chat UI's CSS, copied by the login theme and the site; one token since v3.2.")})
            for token in data["color"]["tokens"]:
                if token["name"] == "focus":
                    for theme in ("light", "dark"):
                        token["value"][theme] = p["focus"][theme]["value"]
                        token.setdefault("srgb", {})[theme] = p["focus"][theme]["srgb"]
        if "case-surface" not in {t["name"] for t in data["color"]["tokens"]}:
            data["color"]["tokens"].append({"name": "case-surface", "value": {}, "usage": (
                "The background of a conversation inside a case (the pane and its header), so a person sees "
                "at a glance that they work in a case, with its documents and colleagues, and not in a "
                "personal conversation. The surface's lightness (light) or surface-alt's (dark) with a little "
                "of the teal's chroma on the teal's hue (tokens v3.3), so every text colour that holds on "
                "those holds here. Never a fill for controls, never behind personal conversations.")})
            for token in data["color"]["tokens"]:
                if token["name"] == "case-surface":
                    for theme in ("light", "dark"):
                        token["value"][theme] = p["case-surface"][theme]["value"]
                        token.setdefault("srgb", {})[theme] = p["case-surface"][theme]["srgb"]
    rows = contrast_table(p)
    for theme, fg, bg, need, by_l, by_wcag in rows:
        if min(by_l, by_wcag) < need:
            problems.append(f"{theme}: {fg} on {bg} is {by_l:.2f}:1 (OKLCH) / {by_wcag:.2f}:1 (WCAG), needs {need}:1")
    if not check:
        data["version"] = "3.3"
        data["colorRules"] = ("tokens/palette.py: one neutral hue (258°), even lightness steps per theme, hover, "
                              "ink and boundary states as fixed lightness offsets on the accent's and the teal's hue, the case "
                              "surface a neutral lightness on the teal's hue; "
                              "every colour here is written by that script, not by hand.")
        data["typeRules"] = ("tokens/palette.py TYPE_SCALE: the text styles every surface may use, by name; a "
                             "surface uses these and nothing else. Written by the script, not by hand.")
        TOKENS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"{'theme':5} {'text':12} {'on':16} {'need':>5} {'OKLCH':>7} {'WCAG':>7}")
        for theme, fg, bg, need, by_l, by_wcag in rows:
            print(f"{theme:5} {fg:12} {bg:16} {need:>5} {by_l:>7.2f} {by_wcag:>7.2f}")
    for problem in problems:
        print(problem, file=sys.stderr)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

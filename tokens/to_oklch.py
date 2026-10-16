"""tokens.json: every colour as OKLCH (the sRGB hex kept beside it). Run from the brand repository root.

Usage: python3 tokens/to_oklch.py            rewrite tokens/tokens.json in place
       python3 tokens/to_oklch.py --check    exit 1 if any OKLCH value doesn't round-trip to its hex

The conversion is Björn Ottosson's OKLab (sRGB, D65). Values are rounded to what still round-trips to
the same sRGB hex: lightness and chroma to 4 decimals, hue to 2.
"""

import json
import math
import re
import sys
from pathlib import Path

TOKENS = Path(__file__).resolve().parent / "tokens.json"


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = min(1.0, max(0.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def rgb_to_oklch(r: float, g: float, b: float) -> tuple[float, float, float]:
    r, g, b = (srgb_to_linear(x) for x in (r, g, b))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (x ** (1 / 3) for x in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    b2 = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    C = math.hypot(a, b2)
    H = math.degrees(math.atan2(b2, a)) % 360 if C > 1e-4 else 0.0
    return L, C, H


def oklch_to_rgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    a, b2 = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = L + 0.3963377774 * a + 0.2158037573 * b2
    m = L - 0.1055613458 * a - 0.0638541728 * b2
    s = L - 0.0894841775 * a - 1.2914855480 * b2
    l, m, s = (x ** 3 for x in (l, m, s))
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(linear_to_srgb(x) for x in (r, g, b))


def parse(value: str) -> tuple[tuple[float, float, float], float | None]:
    """A hex or rgba() colour as (r, g, b in 0..1, alpha or None)."""
    if m := re.fullmatch(r"#([0-9a-fA-F]{6})", value.strip()):
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)), None
    if m := re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)", value.strip()):
        r, g, b, a = m.groups()
        return (int(r) / 255, int(g) / 255, int(b) / 255), (float(a) if a is not None else None)
    raise ValueError(f"not a hex or rgba colour: {value}")


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def oklch_css(value: str) -> str:
    rgb, alpha = parse(value)
    L, C, H = rgb_to_oklch(*rgb)
    text = f"oklch({L:.4f} {C:.4f} {H:.2f})" if alpha is None else f"oklch({L:.4f} {C:.4f} {H:.2f} / {alpha:g})"
    back = to_hex(oklch_to_rgb(round(L, 4), round(C, 4), round(H, 2)))
    if back != to_hex(rgb):
        raise ValueError(f"{value} -> {text} -> {back}: doesn't round-trip")
    return text


def hex_of(value: str) -> str:
    """The sRGB hex kept beside the OKLCH value: a hex as is, an rgba() as hex plus its alpha."""
    rgb, alpha = parse(value)
    return to_hex(rgb) if alpha is None else f"{to_hex(rgb)} / {alpha:g}"


def parse_oklch(value: str) -> tuple[float, float, float, float | None]:
    m = re.fullmatch(r"oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(?:/\s*([\d.]+)\s*)?\)", value.strip())
    if not m:
        raise ValueError(f"not an oklch() colour: {value}")
    L, C, H, a = m.groups()
    return float(L), float(C), float(H), (float(a) if a is not None else None)


def main() -> None:
    data = json.loads(TOKENS.read_text())
    check = "--check" in sys.argv
    problems = []
    for token in data["color"]["tokens"]:
        for theme, value in token["value"].items():
            if value.startswith("{"):  # an alias to another token
                continue
            if check:
                L, C, H, a = parse_oklch(value)
                expected = token["srgb"][theme]
                got = to_hex(oklch_to_rgb(L, C, H)) + (f" / {a:g}" if a is not None else "")
                if got != expected:
                    problems.append(f"{token['name']} ({theme}): {value} is {got}, srgb says {expected}")
                continue
            if value.startswith("oklch("):
                continue
            token.setdefault("srgb", {})[theme] = hex_of(value)
            token["value"][theme] = oklch_css(value)
    if check:
        for p in problems:
            print(p, file=sys.stderr)
        sys.exit(1 if problems else 0)
    data["version"] = 3
    data["colorFormat"] = ("OKLCH (CSS Color 4): value is what goes into CSS; srgb is the same colour as sRGB hex "
                           "(with its alpha), for tools that can't read OKLCH. Lightness 0..1, chroma, hue in degrees.")
    TOKENS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{TOKENS}: colours as OKLCH")


if __name__ == "__main__":
    main()

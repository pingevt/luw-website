"""Generate the "L" favicon set from Fraunces (same face as the page title).

Needs fonttools and the Fraunces variable font:
  curl -L -o Fraunces.ttf "https://github.com/google/fonts/raw/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf"
  python favicon.py Fraunces.ttf ../assets
Writes favicon.svg (switches ink color with the browser's light/dark theme),
light/dark PNG fallbacks, favicon.ico, and an opaque apple-touch-icon.
"""
import subprocess, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

INK_LIGHT = "#0d0b0a"   # glyph on light browser chrome
INK_DARK = "#f1e6d8"    # glyph on dark browser chrome
TILE = "#0d0b0a"        # apple-touch-icon background (iOS needs opaque)

font_path, out = sys.argv[1], sys.argv[2].rstrip("/")
font = instantiateVariableFont(TTFont(font_path), {"wght": 600, "opsz": 72, "SOFT": 100, "WONK": 1})
gs = font.getGlyphSet()
glyph = gs[font.getBestCmap()[ord("L")]]

bp = BoundsPen(gs); glyph.draw(bp)
xmin, ymin, xmax, ymax = bp.bounds
pen = SVGPathPen(gs); glyph.draw(pen)
d = pen.getCommands()

# Fit the glyph into a 64x64 box with a small margin; font units are y-up, so flip.
size, margin = 64, 4
scale = (size - 2 * margin) / max(xmax - xmin, ymax - ymin)
tx = (size - (xmax - xmin) * scale) / 2 - xmin * scale
ty = (size + (ymax - ymin) * scale) / 2 + ymin * scale
transform = f"translate({tx:.2f} {ty:.2f}) scale({scale:.5f} {-scale:.5f})"


def svg(fill=None, tile=None, adaptive=False):
    style = (f"<style>path{{fill:{INK_LIGHT}}}@media (prefers-color-scheme: dark){{path{{fill:{INK_DARK}}}}}</style>"
             if adaptive else "")
    bg = f'<rect width="{size}" height="{size}" rx="14" fill="{tile}"/>' if tile else ""
    fill_attr = f' fill="{fill}"' if fill else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">{style}{bg}'
            f'<path transform="{transform}"{fill_attr} d="{d}"/></svg>')


open(f"{out}/favicon.svg", "w").write(svg(adaptive=True))
for name, fill, tile in (("light", INK_LIGHT, None), ("dark", INK_DARK, None), ("touch", INK_DARK, TILE)):
    open(f"/tmp/fav-{name}.svg", "w").write(svg(fill=fill, tile=tile))

png = lambda src, px, dst: subprocess.run(
    ["magick", "-background", "none", "-density", "600", src, "-resize", f"{px}x{px}", dst], check=True)
png("/tmp/fav-light.svg", 32, f"{out}/favicon-light-32.png")
png("/tmp/fav-dark.svg", 32, f"{out}/favicon-dark-32.png")
png("/tmp/fav-touch.svg", 180, f"{out}/apple-touch-icon.png")
subprocess.run(["magick", "-background", "none", "-density", "600", "/tmp/fav-light.svg",
                "-define", "icon:auto-resize=48,32,16", f"{out}/../favicon.ico"], check=True)
print("favicons written to", out)

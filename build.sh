#!/usr/bin/env bash
# Regenerate site images from src/hero.png (square, 1024px+ ComfyUI render).
# Usage: ./build.sh            (uses src/hero.png)
#        ./build.sh path.png   (copies path.png to src/hero.png first)
set -euo pipefail
cd "$(dirname "$0")"

if [[ $# -gt 0 ]]; then cp "$1" src/hero.png; fi
SRC=src/hero.png
A=assets

for w in 640 1024; do
  magick "$SRC" -resize ${w}x${w} -strip -quality 82 "$A/hero-$w.jpg"
  cwebp -quiet -q 80 -resize $w $w "$SRC" -o "$A/hero-$w.webp"
  avifenc -q 60 -s 6 <(magick "$SRC" -resize ${w}x${w} png:-) "$A/hero-$w.avif" >/dev/null 2>&1 \
    || { magick "$SRC" -resize ${w}x${w} "$A/tmp.png"; avifenc -q 60 -s 6 "$A/tmp.png" "$A/hero-$w.avif" >/dev/null; rm "$A/tmp.png"; }
done

# Favicons are the Fraunces "L", made separately by tools/favicon.py

# Link-preview image: monster on the left, name + tagline on the right, in Fraunces (fonts are OFL)
BG="#0d0b0a"
magick -size 1200x630 "xc:$BG" \
  \( "$SRC" -resize 630x630 \) -gravity west -composite \
  -gravity west -fill "#f1e6d8" -font tools/Fraunces-500.ttf -pointsize 64 \
  -annotate +690-70 "Little Urchin" -annotate +690+10 "Workshop" \
  -fill "#a8917c" -font tools/Fraunces-Italic-400.ttf -pointsize 34 \
  -annotate +692+90 "Craftsmanship, start to finish." \
  -strip -quality 85 "$A/og-image.jpg"

ls -la "$A"

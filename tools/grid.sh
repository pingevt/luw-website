#!/usr/bin/env bash
# Build the workshop-floor grid images + manifest from src/grid.txt (one ComfyUI render id per line).
# Usage: tools/grid.sh [render_dir]   (default: ~/Documents/ComfyUI/output/little-monsters)
set -euo pipefail
cd "$(dirname "$0")/.."
SRC_DIR="${1:-$HOME/Documents/ComfyUI/output/little-monsters}"
OUT=assets/grid
rm -f "$OUT"/*.webp "$OUT"/manifest.json
ids=()
while read -r id; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  f=$(ls "$SRC_DIR/${id}"_*.png 2>/dev/null | head -1) || true
  [[ -z "$f" ]] && { echo "missing: $id" >&2; exit 1; }
  for w in 256 512; do cwebp -quiet -q 78 -resize $w $w "$f" -o "$OUT/$id-$w.webp"; done
  ids+=("\"$id\"")
done < src/grid.txt
(IFS=,; echo "[${ids[*]}]") > "$OUT/manifest.json"
echo "${#ids[@]} grid images -> $OUT ($(du -sh "$OUT" | cut -f1))"

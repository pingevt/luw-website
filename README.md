# littleurchinworkshop.com

Placeholder site for Little Urchin Workshop LLC: one little-monster hero, the name, and the contact email. Static, no build step, hosted on GitHub Pages.

- Swap the hero: `./build.sh path/to/new-render.png` (square ComfyUI render, 1024px+), then commit `src/` + `assets/`
- Hero renders come from the ComfyUI "Little Monsters - hero" workflow. Prompts say "little monster", never "urchin" (that pulls sea-urchin spikes).
- Favicons: the "L" from Fraunces (the title font), light/dark aware. Regenerate with `tools/favicon.py` (instructions at the top of that file).
- Workshop-floor grid: `src/grid.txt` lists the ComfyUI render ids (one per line). `tools/grid.sh` builds `assets/grid/*.webp` + `manifest.json`. The page shows a random 8 (4 on phones) and crossfades one tile about every 5s. A monster never appears twice, and same-seed renders count as the same monster.

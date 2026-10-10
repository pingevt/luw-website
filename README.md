# littleurchinworkshop.com

Bare-bones site for Little Urchin Workshop LLC: name, what LUW does, services, founder, contact, and a privacy page (`privacy.html`). Static, no build step, hosted on GitHub Pages. The earlier little-monster version (hero + cycling grid) lives on the `monsters` branch; the hero/grid notes below apply there.

- Swap the hero: `./build.sh path/to/new-render.png` (square ComfyUI render, 1024px+), then commit `src/` + `assets/`
- Hero renders come from the ComfyUI "Little Monsters - hero" workflow. Prompts say "little monster", never "urchin" (that pulls sea-urchin spikes).
- Favicons: the "L" from Fraunces (the title font), light/dark aware. Regenerate with `tools/favicon.py` (instructions at the top of that file).
- Workshop-floor grid: `src/grid.txt` lists the ComfyUI render ids (one per line). `tools/grid.sh` builds `assets/grid/*.webp` + `manifest.json`. The page shows a random 8 (4 on phones) and crossfades one tile about every 5s. Only one monster per scene (same round + prompt, any seed/wording/cfg) is on screen at a time.
- Picker: `python3 tools/picker.py` builds `tools/picker.html` (gitignored), a contact sheet of every render in `~/Documents/ComfyUI/output/little-monsters/` with in-use badges, filters, hide, picks, and the embedded prompts. Picks/hides live in browser localStorage.

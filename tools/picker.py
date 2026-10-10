"""Build a click-to-pick contact sheet of every little-monster render so far.

Marks what the live site already uses (hero + src/grid.txt in the site repo), and lets
you hide renders you never want to see again. Picks and hides persist in localStorage.
"""
import glob, html, json, os, re, struct


def png_prompt(path):
    """Read the ComfyUI API graph ComfyUI embeds in each PNG's tEXt 'prompt' chunk."""
    try:
        with open(path, "rb") as f:
            f.read(8)
            while True:
                head = f.read(8)
                if len(head) < 8:
                    return None
                n, kind = struct.unpack(">I4s", head)
                data = f.read(n); f.read(4)
                if kind == b"tEXt" and data.startswith(b"prompt\0"):
                    g = json.loads(data.split(b"\0", 1)[1])
                    ks = next(v["inputs"] for v in g.values() if v.get("class_type") == "KSampler")
                    text = lambda ref: g[ref[0]]["inputs"]["text"]
                    return {"pos": text(ks["positive"]), "neg": text(ks["negative"]), "cfg": ks["cfg"], "steps": ks["steps"]}
                if kind == b"IEND":
                    return None
    except Exception:
        return None

OUT = os.path.expanduser("~/Documents/ComfyUI/output/little-monsters")
SITE = os.path.expanduser("~/Projects/luw-website")
HERE = os.path.dirname(os.path.abspath(__file__))
HERO = "r7_lanternpup2_90234162092562"

grid = set()
try:
    grid = {l.strip() for l in open(os.path.join(SITE, "src/grid.txt")) if l.strip() and not l.startswith("#")}
except FileNotFoundError:
    pass

files = sorted(glob.glob(os.path.join(OUT, "r*_*.png")), key=os.path.getmtime)
groups = {}
for f in files:
    m = re.match(r"(r\d+)_([a-z0-9]+)_(\d+)_", os.path.basename(f))
    if m:
        groups.setdefault((m[1], m[2]), []).append((f, m[3]))

sections = ""
for (rnd, variant), items in groups.items():
    cards = ""
    for f, seed in items:
        id_ = f"{rnd}_{variant}_{seed}"
        use = "hero" if id_ == HERO else "grid" if id_ in grid else ""
        badge = f'<span class="badge {use}">{"hero" if use == "hero" else "in grid"}</span>' if use else ""
        pr = png_prompt(f)
        ptxt = (f'<div class="prompt"><b>cfg {pr["cfg"]} · {pr["steps"]} steps</b><br>{html.escape(pr["pos"])}'
                f'<br><span class="neg">neg: {html.escape(pr["neg"])}</span></div>') if pr else ""
        tip = html.escape(pr["pos"], quote=True) if pr else ""
        cards += (f'<figure data-id="{id_}" data-use="{use}" title="{tip}"><img src="file://{html.escape(f)}" loading="lazy">'
                  f'{badge}<button class="hide" title="Hide this one">&times;</button>'
                  f'<figcaption>{rnd} {variant} · {seed}</figcaption>{ptxt}</figure>')
    sections += f'<section><h2>{rnd} · {variant}</h2><main>{cards}</main></section>'

open(os.path.join(HERE, "picker.html"), "w").write(f"""<!doctype html><meta charset=utf-8><title>Little monster picker</title>
<style>
body{{font:14px system-ui;background:#0d0b0a;color:#eee;margin:0 16px 80px}}
h2{{font-weight:500;margin:24px 0 8px;opacity:.7}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}}
figure{{margin:0;cursor:pointer;border-radius:10px;outline:3px solid transparent;outline-offset:2px;position:relative}}
figure.on{{outline-color:#e09a5f}}
figure.hidden{{display:none}}
body.show-hidden figure.hidden{{display:block;opacity:.3}}
img{{width:100%;border-radius:8px;display:block}}
figcaption{{padding:4px 2px;opacity:.7;font-size:12px}}
.badge{{position:absolute;top:8px;left:8px;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;background:#e09a5f;color:#1a120c}}
.badge.hero{{background:#f1e6d8}}
.hide{{position:absolute;top:6px;right:6px;width:28px;height:28px;border-radius:50%;border:0;background:#000a;color:#fff;font-size:18px;line-height:1;cursor:pointer;opacity:0;transition:opacity .15s}}
figure:hover .hide{{opacity:1}}
figure.hidden .hide{{opacity:1;background:#e09a5f;color:#000}}
#bar{{position:sticky;top:0;z-index:2;background:#0d0b0aee;padding:12px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
#bar code{{color:#e09a5f;word-break:break-all;flex-basis:100%}}
button.b{{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid #555;background:#222;color:#eee;cursor:pointer}}
button.b.active{{border-color:#e09a5f;color:#e09a5f}}
section.empty{{display:none}}
.prompt{{display:none;font-size:11px;line-height:1.4;color:#cbb;padding:2px 2px 8px}}
.prompt .neg{{color:#776}}
body.show-prompts .prompt{{display:block}}
</style>
<div id=bar>
  <strong>Picked: <span id=n>0</span></strong>
  <button class=b id=copy>Copy picks</button><button class=b id=clear>Clear picks</button>
  <span style="opacity:.5">|</span>
  <button class="b f active" data-f=all>All</button><button class="b f" data-f=used>In use</button><button class="b f" data-f=unused>Not in use</button>
  <span style="opacity:.5">|</span>
  <button class=b id=showhidden>Show hidden (<span id=hn>0</span>)</button><button class=b id=showprompts>Show prompts</button>
  <code id=list></code>
</div>
{sections}
<script>
const get=(k)=>{{try{{return JSON.parse(localStorage.getItem(k)||'[]')}}catch(e){{return[]}}}};
const put=(k,v)=>{{try{{localStorage.setItem(k,JSON.stringify(v))}}catch(e){{}}}};
let picks=get('lm-picks'), hidden=get('lm-hidden'), filter='all';
const figs=[...document.querySelectorAll('figure')];
const render=()=>{{
  figs.forEach(f=>{{
    const id=f.dataset.id, used=!!f.dataset.use;
    f.classList.toggle('on',picks.includes(id));
    f.classList.toggle('hidden',hidden.includes(id));
    f.style.display=(filter==='used'&&!used)||(filter==='unused'&&used)?'none':'';
  }});
  document.querySelectorAll('section').forEach(s=>s.classList.toggle('empty',![...s.querySelectorAll('figure')].some(f=>f.style.display!=='none'&&(!f.classList.contains('hidden')||document.body.classList.contains('show-hidden')))));
  n.textContent=picks.length; list.textContent=picks.join(', '); hn.textContent=hidden.length;
  put('lm-picks',picks); put('lm-hidden',hidden);
}};
figs.forEach(f=>{{
  f.onclick=()=>{{const id=f.dataset.id;picks=picks.includes(id)?picks.filter(p=>p!==id):[...picks,id];render()}};
  f.querySelector('.hide').onclick=(e)=>{{e.stopPropagation();const id=f.dataset.id;hidden=hidden.includes(id)?hidden.filter(h=>h!==id):[...hidden,id];render()}};
}});
document.querySelectorAll('.f').forEach(b=>b.onclick=()=>{{filter=b.dataset.f;document.querySelectorAll('.f').forEach(x=>x.classList.toggle('active',x===b));render()}});
showhidden.onclick=()=>{{document.body.classList.toggle('show-hidden');showhidden.classList.toggle('active');render()}};
showprompts.onclick=()=>{{document.body.classList.toggle('show-prompts');showprompts.classList.toggle('active')}};
copy.onclick=()=>navigator.clipboard.writeText(picks.join(', '));
clear.onclick=()=>{{picks=[];render()}};
render();
</script>""")
print(f"{len(files)} renders ({len(grid)} in grid + hero) ->", os.path.join(HERE, "picker.html"))

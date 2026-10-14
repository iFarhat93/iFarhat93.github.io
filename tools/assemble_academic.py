"""Assemble the academic site (academicpages look) as one page with four windows: About, Publications, PhD, Contact.

The PhD window reuses the story page's hero, scenes, record and script; the rest is built here from content/phd.json.
Writes work/artifact/academic.html (fragment for claude.ai) and work/academic-local.html (full document for local checks).
"""
import json, re, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
story = (ROOT / 'tools' / 'pages' / 'story.html').read_text(encoding='utf-8')
phd = json.loads((ROOT / 'content' / 'phd.json').read_text(encoding='utf-8'))

def between(s, a, b, inclusive=True):
    i = s.index(a); j = s.index(b, i) + (len(b) if inclusive else 0)
    return s[i:j]

hero = between(story, '<header class="hero"', '</header>')
hero = re.sub(r'\s*<div class="mosaic"[^>]*></div>', '', hero)
hero = hero.replace('<div class="eyebrow">PhD · INSA Rennes / IETR · 2019 – 2022</div>', '<div class="eyebrow">PhD · INSA Rennes / IETR · 2019 – 2022</div>')
main = between(story, '<main>', '</main>')
record = between(story, '<section class="record" id="record">', '</section>')
record = record.replace('<h2 style="margin-top:6px">The record, for reference</h2>', '<h2>The record, for reference</h2>')
LINK = re.compile(r'\s*<a class="btn[^"]*" href="(?:explainer|platforms)\.html[^"]*">[^<]*</a>')
hero, main, record = LINK.sub('', hero), LINK.sub('', main), LINK.sub('', record)
assert 'explainer.html' not in hero + main + record and 'platforms.html' not in hero + main + record, 'cross-links remain'
audio = '<audio id="aud" preload="none"></audio>'
three = re.search(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^>]*></script>', story).group(0)
script = re.search(r'<script>\s*\(function\(\)\{.*?\}\)\(\);\s*</script>', story, re.S).group(0)
durations = {}
for cues in sorted((ROOT / 'work' / 'audio').glob('scene-*.cues.json')):
    sid = cues.stem.split('-')[1].split('.')[0]
    if (ROOT / 'docs' / 'assets' / 'audio' / f'scene-{sid}.mp3').exists():
        durations[sid] = round(json.loads(cues.read_text(encoding='utf-8')).get('duration', 0))
script = script.replace('__SCENE_AUDIO__', json.dumps(durations))
assert '__SCENE_AUDIO__' not in script and durations, 'scene audio durations missing'

# ---------- publications from phd.json ----------
def pub_entry(p):
    links = []
    if p.get('doi'): links.append(f'[<a href="https://doi.org/{H.escape(p["doi"])}" target="_blank" rel="noopener">doi</a>]')
    if p.get('open'):
        lab = 'arxiv' if 'arxiv' in p['open'] else 'hal' if 'hal.' in p['open'] else 'open access'
        links.append(f'[<a href="{H.escape(p["open"])}" target="_blank" rel="noopener">{lab}</a>]')
    return (f'<blockquote class="pub"><span class="authors">{H.escape(p["authors"])}</span>, “<b>{H.escape(p["title"])}</b>”, '
            f'<span class="venue">{H.escape(p["venue"])}</span>. {" ".join(links)}</blockquote>')
years = sorted({p['year'] for p in phd['publications']}, reverse=True)
pubs_html = ''
for y in years:
    pubs_html += f'<h2>{y}</h2>' + ''.join(pub_entry(p) for p in phd['publications'] if p['year'] == y)
r = phd['record']
thesis_html = (f'<h2 id="thesis">My thesis</h2><blockquote class="pub"><b>{H.escape(phd["title"])}</b>. {H.escape(r["institution"].split(" — ")[0])}, '
               f'defended {H.escape(r["defense_date"])}. [<a href="{H.escape(r["hal_url"])}" target="_blank" rel="noopener">manuscript, open access</a>] '
               f'[<a href="{H.escape(r["theses_fr_url"])}" target="_blank" rel="noopener">theses.fr</a>] [<a href="#phd">the explainer</a>]</blockquote>'
               f'<p class="abstract"><b>Abstract.</b> {H.escape(phd["abstract"])}</p>')

CSS = r'''
/* Layout: the academicpages shell (masthead nav, left author sidebar, 925px content column) with four windows switched by tabs; the PhD window carries the 3D story. */
:root{
  --bg:#ffffff; --fg:#494e52; --head:#000000; --muted:#9ba1a6; --line:#f2f3f3; --line-2:#e6e8ea; --link:#52adc8; --accent:#52adc8; --accent-ink:#ffffff;
  --surface:#ffffff; --surface-2:#f7f8f8; --shadow:rgba(0,0,0,.08);
  --c3-die:#3d4348; --c3-pin:#aab0b5; --c3-block:#b3b9be; --c3-accent:#52adc8; --c3-glow:#9fdcee; --c3-blue:#586e75; --c3-green:#cb4b16;
  --c3-dim:#e3e6e8; --c3-y:#b3b9be; --c3-cr:#f89406; --c3-cb:#52adc8; --c3-rail:#e9ebed; --bar:#bdc1c4;
  --sans:-apple-system,"Segoe UI",Roboto,"Helvetica Neue","Lucida Grande",Arial,sans-serif; --mono:Monaco,Consolas,"Lucida Console",monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){ --bg:#1b1f22; --fg:#dfe3e6; --head:#ffffff; --muted:#9ba1a6; --line:#2c3236; --line-2:#363c41; --link:#6cc1d9; --accent:#6cc1d9; --accent-ink:#0e1a1f;
    --surface:#22272b; --surface-2:#2a3034; --shadow:rgba(0,0,0,.4); --c3-block:#55606a; --c3-dim:#2e353a; --c3-y:#55606a; --c3-rail:#2a3034; --bar:#55606a; color-scheme:dark }
}
:root[data-theme="dark"]{ --bg:#1b1f22; --fg:#dfe3e6; --head:#ffffff; --muted:#9ba1a6; --line:#2c3236; --line-2:#363c41; --link:#6cc1d9; --accent:#6cc1d9; --accent-ink:#0e1a1f;
    --surface:#22272b; --surface-2:#2a3034; --shadow:rgba(0,0,0,.4); --c3-block:#55606a; --c3-dim:#2e353a; --c3-y:#55606a; --c3-rail:#2a3034; --bar:#55606a; color-scheme:dark }

*{box-sizing:border-box}
html{font-size:18px}
@media (max-width:64em){ html{font-size:16px} }
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);line-height:1.5}
a{color:var(--link)}
h1,h2,h3{font-family:var(--sans);font-weight:700;color:var(--head);line-height:1.2;margin:2em 0 .5em;text-wrap:balance}
h2{font-size:1.3em} h3{font-size:1.05em}
p{margin:0 0 1em}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--link);outline-offset:2px}
[hidden]{display:none!important}
.mono{font-family:var(--mono)}
.eyebrow{font-size:.78em;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}

/* masthead */
.masthead{border-bottom:1px solid var(--line)}
.masthead__inner{max-width:925px;margin:0 auto;padding:1em;display:flex;align-items:center;justify-content:space-between;gap:1em;flex-wrap:wrap}
.site-title{font-weight:700;color:var(--head);text-decoration:none;font-size:1.05em}
.nav{display:flex;gap:1.3em;flex-wrap:wrap}
.nav a{color:var(--head);text-decoration:none;font-size:.92em;padding:.25em 0;border-bottom:2px solid transparent}
.nav a:hover{color:var(--link)}
.nav a.active{border-bottom-color:var(--link)}

/* main grid */
#main{max-width:925px;margin:2em auto;padding:0 1em;display:grid;grid-template-columns:200px minmax(0,1fr);gap:2.2em;align-items:start}
.sidebar{position:sticky;top:1em;font-size:.86em}
.author__avatar img,.author__avatar .initials{width:110px;height:110px;border-radius:50%;display:block;object-fit:cover}
.author__avatar .initials{background:var(--surface-2);border:1px solid var(--line-2);color:var(--head);font-weight:700;font-size:2.2em;display:grid;place-items:center}
.author__name{font-size:1.25em;margin:.6em 0 0;font-weight:700}
.author__bio{color:var(--muted);margin:.2em 0 0}
.author__urls{list-style:none;margin:.9em 0 0;padding:0}
.author__urls li{margin:.35em 0;display:flex;align-items:center;gap:.5em}
.author__urls a{color:var(--fg);text-decoration:none}
.author__urls a:hover{color:var(--link)}
.author__urls svg{width:16px;height:16px;fill:currentColor;flex:0 0 auto}
.author__urls .lbl{font-size:.8em;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-top:.4em}
.content{min-width:0}
.page__title{font-size:2em;line-height:1;margin:0 0 .6em}
.panel{min-width:0}
.news{list-style:none;padding:0;margin:0}
.news li{display:grid;grid-template-columns:5.2em minmax(0,1fr);gap:.8em;margin:.45em 0}
.news .date{color:var(--muted);font-size:.9em;padding-top:.1em}
.interests{padding-left:1.2em;margin:0}
.interests li{margin:.25em 0}
blockquote.pub{margin:1em 0;padding:0 0 0 1em;border-left:.25em solid var(--line-2);font-style:normal}
blockquote.pub .authors{color:var(--fg)}
blockquote.pub .venue{font-style:italic}
.abstract{font-size:.92em;color:var(--fg)}
.contact dl{display:grid;grid-template-columns:7em minmax(0,1fr);gap:.5em 1em;margin:0}
.contact dt{color:var(--muted)} .contact dd{margin:0;display:flex;gap:.6em;align-items:center;flex-wrap:wrap}
.copy{border:1px solid var(--line-2);background:var(--surface);border-radius:4px;padding:.15em .6em;font-size:.8em;cursor:pointer}
.copy:hover{border-color:var(--link);color:var(--link)}
.page__footer{max-width:925px;margin:3em auto 0;padding:1.5em 1em;border-top:1px solid var(--line);color:var(--muted);font-size:.8em}
@media (max-width:64em){
  #main{grid-template-columns:1fr}
  .sidebar{position:static;display:grid;grid-template-columns:110px minmax(0,1fr);gap:1em;align-items:start}
  .author__name{margin-top:0}
}

/* ---- PhD window: the story (hero, scenes, record) ---- */
.btn{border:1px solid var(--line-2);background:var(--surface);color:var(--fg);padding:.5em .9em;border-radius:4px;cursor:pointer;display:inline-flex;align-items:center;gap:.5em;line-height:1.2;text-decoration:none;font-size:.9em;font-weight:600}
.btn:hover{border-color:var(--link);color:var(--link)}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn.primary:hover{filter:brightness(.95);color:var(--accent-ink)}
.btn.small{padding:.35em .7em;font-size:.82em}
.hero{padding:0 0 1.5em;border-bottom:1px solid var(--line)}
.hero .wrap{display:grid;gap:1.2em}
.hero h1{font-size:1.6em;margin:.3em 0 0;line-height:1.15}
.hero p.lede{margin:.8em 0 0;font-size:1em}
.hero p.who{color:var(--muted);font-size:.9em;margin:.5em 0 0}
.hero .cta{display:flex;flex-wrap:wrap;gap:.6em;margin-top:1em}
.hero3d{position:relative}
.hero3d .c3d{height:clamp(260px,40vw,380px)}
.legend{display:flex;flex-wrap:wrap;gap:1em;font-size:.82em;color:var(--muted);margin-top:.5em}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:.4em}
.hint{font-size:.7em;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);position:absolute;right:.6em;top:.5em;z-index:2}
.c3d{position:relative;width:100%;height:360px;min-width:0;touch-action:pan-y;cursor:grab;overflow:hidden;border:1px solid var(--line-2);border-radius:4px;background:var(--surface-2)}
.c3d:active{cursor:grabbing}
.c3d canvas{display:block;position:relative;image-rendering:-moz-crisp-edges;image-rendering:crisp-edges;image-rendering:pixelated}
.c3d.no3d::after{content:"3D view needs WebGL; the figures in “Go deeper” show the same thing.";position:absolute;inset:0;display:grid;place-items:center;color:var(--muted);font-size:.9em;padding:1em;text-align:center}
.l3d{position:absolute;left:0;top:0;transform:translate(-50%,-50%);pointer-events:none;font-size:.68em;padding:.2em .5em;border-radius:3px;background:color-mix(in oklab,var(--surface) 90%,transparent);color:var(--head);border:1px solid var(--line-2);white-space:nowrap;will-change:transform}
.l3d.acc{border-color:var(--accent);color:var(--accent);font-weight:600}
.stage-label{position:absolute;left:.7em;bottom:.6em;font-size:.8em;background:color-mix(in oklab,var(--surface) 92%,transparent);border:1px solid var(--line-2);border-radius:3px;padding:.3em .6em;max-width:calc(100% - 1.4em)}
.stage-tools{position:absolute;right:.6em;top:.5em;display:flex;gap:.3em;z-index:2}
.stage-tools button{border:1px solid var(--line-2);background:color-mix(in oklab,var(--surface) 92%,transparent);border-radius:3px;padding:.25em .5em;font-size:.72em;cursor:pointer}
.stage-tools button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.scene{padding:2em 0 1.6em;border-bottom:1px solid var(--line)}
.scene .wrap{display:grid;gap:1.2em}
.scene .visual{min-width:0;display:grid;gap:.8em}
.scene .visual figure{margin:0;background:var(--surface);border:1px solid var(--line-2);border-radius:4px;padding:.6em;min-width:0}
.scene .visual figure svg{width:100%;height:auto;display:block}
.scene .visual figcaption{font-size:.8em;color:var(--muted);margin-top:.4em;line-height:1.4}
.scene .text{min-width:0}
.scene .num{font-size:.78em;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.scene h2{margin:.3em 0 .4em;font-size:1.35em}
.scene p.say{font-size:1em;margin:0}
.scene .tools{display:flex;flex-wrap:wrap;gap:.5em;margin-top:.9em;align-items:center}
.deeper{margin-top:1em;border:1px solid var(--line-2);border-radius:4px;background:var(--surface);padding:0 1em}
.deeper summary{cursor:pointer;padding:.7em 0;font-weight:700;list-style:none;display:flex;justify-content:space-between;align-items:center;color:var(--head)}
.deeper summary::-webkit-details-marker{display:none}
.deeper summary::after{content:"+";color:var(--muted)}
.deeper[open] summary::after{content:"−"}
.deeper ul{margin:0;padding:0 0 .8em 1.2em;display:grid;gap:.4em;font-size:.9em}
.deeper figure{margin:0 0 .8em;background:var(--surface-2);border:1px solid var(--line-2);border-radius:4px;padding:.5em}
.deeper figure img{display:block;width:100%;height:auto}
.deeper figcaption{font-size:.78em;color:var(--muted);margin-top:.4em;line-height:1.4}
.deeper .src{font-size:.8em;color:var(--muted);padding-bottom:.8em}
.deeper .src b{color:var(--fg)}
.chart .lbl{fill:var(--fg);font-family:var(--sans);font-size:12.5px}
.chart .val{fill:var(--head);font-family:var(--mono);font-size:12px}
.chart .small{fill:var(--muted);font-family:var(--sans);font-size:11px}
.chart .bar{fill:var(--bar);stroke:none}
.chart .bar.emph{fill:var(--accent)}
.chart .bar.blue{fill:var(--c3-blue)}
.chart .axis{stroke:var(--line-2);stroke-width:1.5}
.chart .grid{stroke:var(--line-2);stroke-dasharray:2 3}
.pipe text{font-family:var(--sans);font-size:12px;fill:var(--fg)}
.pipe .small{font-size:10.5px;fill:var(--muted)}
.pipe .box{fill:var(--surface);stroke:var(--fg);stroke-width:1.1}
.pipe .box.hl{stroke:var(--accent);stroke-width:2.4;fill:color-mix(in oklab,var(--accent) 16%,var(--surface));animation:pulse 2.4s ease-in-out infinite}
.pipe .arrow{stroke:var(--fg);stroke-width:1.2;fill:none}
.pipe .dash{stroke:var(--muted);stroke-dasharray:4 4;fill:none}
.pipe .dot{fill:var(--c3-blue)} .pipe .dot.acc{fill:var(--accent)}
@keyframes pulse{0%,100%{stroke-opacity:1}50%{stroke-opacity:.45}}
.gauge{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:.6em;align-items:center;font-size:.8em;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.gauge .track{height:12px;background:var(--surface-2);overflow:hidden;border:1px solid var(--line-2);border-radius:3px}
.gauge .track i{display:block;height:100%;background:var(--accent);width:0;transition:width .15s linear}
.gauge .val{min-width:7em;text-align:right;text-transform:none;letter-spacing:0;color:var(--head);font-family:var(--mono)}
.numbers{border:1px solid var(--line-2);border-radius:4px;background:var(--surface);padding:.8em 1em}
.numbers ul{margin:.4em 0 0;padding-left:1.2em;display:grid;gap:.3em;font-size:.9em}
.record{padding:1.5em 0 0}
.record h2{margin-top:1em}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.7em;margin-top:.5em}
.card{border:1px solid var(--line-2);border-radius:4px;background:var(--surface);padding:.8em 1em;min-width:0}
.card .n{font-weight:700;color:var(--head)}
.card .r{font-size:.75em;text-transform:uppercase;letter-spacing:.04em;color:var(--accent);margin-top:.2em}
.card .a{font-size:.85em;color:var(--muted);margin-top:.2em}
.kv{display:grid;grid-template-columns:7.5em minmax(0,1fr);gap:.4em .8em;font-size:.9em;margin:.8em 0 0}
.kv dt{color:var(--muted)} .kv dd{margin:0}
.pubs{list-style:none;margin:.6em 0 0;padding:0}
.pubs li{display:grid;grid-template-columns:3.2em minmax(0,1fr);gap:.6em;font-size:.9em;padding:.5em 0;border-bottom:1px solid var(--line)}
.pubs .tag{color:var(--muted)}
.links{display:flex;flex-wrap:wrap;gap:.6em;margin-top:1em}

/* 2D animated figures */
.anim{position:relative}
.anim svg{width:100%;height:auto;display:block}
.anim text{font-family:var(--body);font-size:12px;fill:var(--fg)}
.anim .small{font-size:10.5px;fill:var(--muted)}
.anim .b{font-weight:700}
.anim .val{font-family:var(--mono);font-size:12px;fill:var(--fg)}
.anim .bar{fill:var(--bar)} .anim .bar.emph{fill:var(--accent)}
.anim .axis{stroke:var(--line);stroke-width:1.5}
.anim .grid{fill:none;stroke:var(--line);stroke-width:1}
.anim .cell{fill:var(--accent)} .anim .cell.centre{stroke:var(--fg);stroke-width:1.5}
.anim .box{fill:var(--surface-2);stroke:var(--fg);stroke-width:1.2}
.anim .glow{fill:var(--accent);opacity:0}
.anim .sample{fill:var(--accent)} .anim .res{fill:var(--c3-green)}
.anim .mcell{fill:var(--accent);fill-opacity:.25;stroke:var(--line);stroke-width:1}
.anim .beam{stroke:var(--c3-blue);stroke-width:3;opacity:0}
.anim .stage-tools{position:static;margin:8px 0 2px;flex-wrap:wrap;justify-content:flex-start}
.anim .lane{stroke:var(--line);stroke-width:1;stroke-dasharray:3 4}
.anim .tile.dim{fill:var(--c3-dim)} .anim .tile.y{fill:var(--c3-y)} .anim .tile.cr{fill:var(--c3-cr)} .anim .tile.cb{fill:var(--c3-cb)} .anim .tile.held{stroke:var(--accent);stroke-width:2.5}
@media (prefers-reduced-motion: reduce){ *{transition:none!important} .pipe .box.hl{animation:none} }
'''

ICONS = {
 'pin': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1 2.4V18h16V7.4l-8 5.6-8-5.6zM5.4 7l6.6 4.6L18.6 7H5.4z"/></svg>',
 'in': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3h16a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm3.3 6.4H5.2V19h2.1V9.4zM6.3 5.3a1.3 1.3 0 1 0 0 2.6 1.3 1.3 0 0 0 0-2.6zM19 13.6c0-2.9-1.6-4.4-3.7-4.4-1.6 0-2.4.9-2.8 1.5V9.4h-2.1V19h2.1v-5.3c0-1.4.7-2.2 1.9-2.2s1.6.9 1.6 2.2V19H19v-5.4z"/></svg>',
 'cap': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 1 9l11 6 9-4.9V17h2V9L12 3zm-6 10.6V17c0 1.7 2.7 3 6 3s6-1.3 6-3v-3.4l-6 3.3-6-3.3z"/></svg>',
 'hf': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16zM8.5 9a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6zm7 0a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6zM7.6 13.4h8.8c-.4 2.3-2.2 3.8-4.4 3.8s-4-1.5-4.4-3.8z"/></svg>',
 'git': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.2-3.4-1.2-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></svg>',
}

def page(name, email):
    email_html = H.escape(email)
    return f'''<title>Ibrahim Farhat</title>
<style>{CSS}</style>
<!-- body -->
<header class="masthead"><div class="masthead__inner">
  <a class="site-title" href="#about">Ibrahim Farhat</a>
  <nav class="nav" aria-label="Pages"><a href="#about" data-tab="about">About</a><a href="#publications" data-tab="publications">Publications</a><a href="#phd" data-tab="phd">PhD</a><a href="#contact" data-tab="contact">Contact</a></nav>
</div></header>

<div id="main">
  <aside class="sidebar">
    <div class="author__avatar"><img id="avatar" src="assets/profile.jpg" alt="Ibrahim Farhat"><div class="initials" id="initials" hidden>IF</div></div>
    <div>
      <h3 class="author__name">Ibrahim Farhat</h3>
      <p class="author__bio">Senior R&amp;D Researcher at <a href="https://www.tii.ae/" target="_blank" rel="noopener">TII</a>, AIDRC.</p>
      <ul class="author__urls">
        <li class="lbl">Follow</li>
        <li>{ICONS['pin']}<span>Abu Dhabi, UAE</span></li>
        <li>{ICONS['cap']}<a href="https://scholar.google.com/citations?user=6gbNelQAAAAJ&amp;hl=fr&amp;oi=ao" target="_blank" rel="noopener">Google Scholar</a></li>
        <li>{ICONS['in']}<a href="https://www.linkedin.com/in/ibrahim-farhat-470755115/" target="_blank" rel="noopener">LinkedIn</a></li>
        <li>{ICONS['git']}<a href="https://github.com/iFarhat93" target="_blank" rel="noopener">GitHub</a></li>
        <li>{ICONS['hf']}<a href="https://huggingface.co/ifarhatTII" target="_blank" rel="noopener">Hugging Face</a></li>
        <li>{ICONS['mail']}<a href="#contact">Email</a></li>
      </ul>
    </div>
  </aside>

  <div class="content">
    <section class="panel" id="panel-about">
      <h1 class="page__title">About me</h1>
      <p>I am a Senior R&amp;D Researcher at the <a href="https://www.tii.ae/" target="_blank" rel="noopener">Technology Innovation Institute</a> (TII) in Abu Dhabi, in the AI and Digital Science Research Center (AIDRC). I did my PhD at INSA Rennes, in the IETR laboratory, on hardware designs for the new coding tools of the VVC / H.266 standard, built for a real-time 4K encoder and decoder chip, and I defended it in May 2022.</p>
      <p>Since then I have moved to AI, worked on 3D reconstruction with NeRF and 3D Gaussian splatting, edge AI and model compression for the Falcon LLM models, and now models and systems for robotic VLAs and agentic coding for robots. The <a href="#phd">PhD</a> page explains the thesis in ten short scenes, with more depth where you want it.</p>
      <h2>News</h2>
      <ul class="news">
        <li><span class="date">2026</span><span>Q-Codec, reinforcement-learning-based adaptive encoding for immersive aerial video, accepted at IEEE WCNC 2026; ALRM, an agentic LLM for robotic manipulation, on arXiv.</span></li>
        <li><span class="date">2025</span><span>The Falcon-H1 technical report is out; the results of our 360° video super-resolution challenge are published in Signal Processing: Image Communication.</span></li>
        <li><span class="date">2024</span><span>ODVISTA, our omnidirectional video dataset for super-resolution and quality enhancement, accepted at IEEE ICIP 2024.</span></li>
        <li><span class="date">2024</span><span>Our survey on real-time immersive aerial video streaming is published in the IEEE Open Journal of the Communications Society.</span></li>
        <li><span class="date">05/2022</span><span>Defended my PhD at INSA Rennes.</span></li>
      </ul>
      <h2>Main research interests</h2>
      <ul class="interests">
        <li>Edge AI and robotic models.</li>
      </ul>
    </section>

    <section class="panel" id="panel-publications" hidden>
      <h1 class="page__title">Publications</h1>
      <p>Also on <a href="https://scholar.google.com/citations?user=6gbNelQAAAAJ&amp;hl=fr&amp;oi=ao" target="_blank" rel="noopener">Google Scholar</a>.</p>
      {pubs_html}
      {thesis_html}
    </section>

    <section class="panel" id="panel-phd" hidden>
      <h1 class="page__title">My PhD</h1>
      {hero}
      <div id="rail" hidden></div>
      {main}
      {record}
    </section>

    <section class="panel contact" id="panel-contact" hidden>
      <h1 class="page__title">Get in touch</h1>
      <p>The simplest way is email; LinkedIn messages reach me too.</p>
      <dl>
        <dt>Email</dt><dd><span class="mono" id="email">{email_html}</span><button class="copy" id="copyEmail">copy</button><span id="copied" class="eyebrow" hidden>copied</span></dd>
        <dt>LinkedIn</dt><dd><a href="https://www.linkedin.com/in/ibrahim-farhat-470755115/" target="_blank" rel="noopener">ibrahim-farhat</a></dd>
        <dt>Scholar</dt><dd><a href="https://scholar.google.com/citations?user=6gbNelQAAAAJ&amp;hl=fr&amp;oi=ao" target="_blank" rel="noopener">publications and citations</a></dd>
        <dt>GitHub</dt><dd><a href="https://github.com/iFarhat93" target="_blank" rel="noopener">iFarhat93</a></dd>
        <dt>Hugging Face</dt><dd><a href="https://huggingface.co/ifarhatTII" target="_blank" rel="noopener">ifarhatTII</a></dd>
      </dl>
    </section>
  </div>
</div>

<footer class="page__footer">© 2026 Ibrahim Farhat.</footer>
{audio}
{three}
{script}
<script>
(function(){{
  const tabs = ['about', 'publications', 'phd', 'contact'];
  const links = Array.from(document.querySelectorAll('.nav a[data-tab]'));
  function show(tab){{
    tabs.forEach(t => {{ document.getElementById('panel-' + t).hidden = (t !== tab); }});
    links.forEach(a => a.classList.toggle('active', a.dataset.tab === tab));
    document.title = (tab === 'about' ? 'Ibrahim Farhat' : {{publications: 'Publications', phd: 'My PhD', contact: 'Contact'}}[tab] + ' · Ibrahim Farhat');
  }}
  function route(){{
    const h = (location.hash || '#about').slice(1);
    if (tabs.includes(h)) {{ show(h); window.scrollTo({{top: 0}}); return; }}
    const el = document.getElementById(h);
    if (el) {{ const panel = el.closest('.panel'); if (panel) show(panel.id.replace('panel-', '')); el.scrollIntoView({{block: 'start'}}); return; }}
    show('about');
  }}
  window.addEventListener('hashchange', route); route();
  const img = document.getElementById('avatar');
  img.addEventListener('error', () => {{ img.hidden = true; document.getElementById('initials').hidden = false; }});
  if (img.complete && img.naturalWidth === 0) {{ img.hidden = true; document.getElementById('initials').hidden = false; }}
  const btn = document.getElementById('copyEmail');
  btn.addEventListener('click', () => {{
    const t = document.getElementById('email').textContent, ok = () => {{ const c = document.getElementById('copied'); c.hidden = false; setTimeout(() => c.hidden = true, 1500); }};
    const sel = () => {{ const r = document.createRange(); r.selectNodeContents(document.getElementById('email')); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }};
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, sel); else sel();
  }});
}})();
</script>
'''

out = page('Ibrahim Farhat', 'brahim.farhat.co@gmail.com')
(ROOT / 'work' / 'artifact').mkdir(parents=True, exist_ok=True)
(ROOT / 'work' / 'artifact' / 'academic.html').write_text(out, encoding='utf-8')
head, body = out.split('<!-- body -->', 1)
local = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
         '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>' + head + '</head><body>' + body + '</body></html>')
(ROOT / 'work' / 'academic-local.html').write_text(local, encoding='utf-8')
print('academic page', len(out) // 1024, 'KB; publications', len(phd['publications']), 'years', years)

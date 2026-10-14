# Ibrahim Farhat — academic site

A small static site with four windows: **About**, **Publications**, **PhD** and **Contact**. The PhD window explains
the thesis *Efficient hardware designs of the new Versatile Video Coding (VVC) tools for ASIC platforms*
(INSA Rennes / IETR, defended 31 May 2022, HAL `tel-04477217`) in ten scenes, with animated figures, a “Go deeper”
fold under each scene and an optional voice-over.

The site is served as is from `docs/` by GitHub Pages: https://ifarhat93.github.io/ibrahimfarhat/

| path | what it is |
|------|------------|
| `docs/index.html` | The whole site, one page. The windows are hash routes: `#about`, `#publications`, `#phd`, `#contact`. |
| `docs/assets/` | The photo, the thesis figures used in the PhD window, and the ten narration MP3s. |

Everything is relative paths and static files: no build step is needed to serve it, and the page works from disk,
from `python -m http.server --directory docs`, or from GitHub Pages. The only external resource is three.js from
cdnjs, loaded with a subresource-integrity hash.

## Publish on GitHub Pages

```powershell
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main`,
folder: `/docs` → Save.** The site appears at `https://<you>.github.io/<repo>/` a minute later.
`docs/.nojekyll` is there so GitHub serves the files untouched.

## How it is built

```
content/        what a human writes
  phd.json        record, people, organisations, timeline, publications, news, sources
  story.json      the ten scene narrations
  steps.json      the 21-step walkthrough (preview only)
  glossary.json   terms and one-line definitions (preview only)
tools/          the pipeline
  pages/story.html        the story: hero with the chip model, ten scenes, animated SVG figures, record
  assemble_academic.py    builds the site: docs/index.html (and work/artifact/academic.html for claude.ai)
  make_audio.py           narration MP3 + sentence timings (edge-tts, free neural voices), only for changed text
  scan_pdf.py             page thumbnails + an index of every figure/table caption of a PDF
  extract_figures.py      crops each figure to PNG by locating its caption
  build_site.py           development previews in work/preview/: the story alone, the narrated walkthrough
                          (template.html + steps.json) and the Silicon Ladder (pages/platforms.html); not published
docs/           the published site (committed)
work/, site/    intermediate outputs (ignored)
sources/        the manuscript, papers and metadata, kept local only (ignored; the manuscript and papers are open access on HAL/arXiv)
```

Rebuild after any change:

```powershell
# figures (once per thesis)
uv run --python 3.12 --with pymupdf python -I tools/scan_pdf.py sources/thesis/<thesis>.pdf work/thumbs
uv run --python 3.12 --with pymupdf python -I tools/extract_figures.py sources/thesis/<thesis>.pdf work/thumbs/captions.json work/figures 160
# voice-over (only narrations whose text changed are re-synthesised)
uv run --python 3.12 --with edge-tts python -I tools/make_audio.py --set story
# the site
python -I tools/assemble_academic.py
```

## Reusing it for another PhD

1. Put the manuscript in `sources/thesis/` and run the two figure commands; `work/thumbs/captions.json` lists every
   figure with its page.
2. Fill `content/phd.json` from the HAL / theses.fr record (the HAL REST API is open; the HTML pages are bot-walled,
   `curl -A "curl/8.4.0"` fetches the PDF).
3. Write `content/story.json` (the ten narrations) and adapt the scenes and figures in `tools/pages/story.html` to
   the thesis's own mechanisms; edit the About, News and Contact text in `tools/assemble_academic.py`.
4. Generate the audio, build, push.

## What is public here, and what is not

The site names the academic supervision (directors and supervisor at INSA Rennes / IETR) and refers to the
industrial partner without naming it or its staff. Published co-author lists in the publications section are
reproduced as printed. The source material under `sources/` is never committed.

## Sources

Thesis manuscript (HAL tel-04477217); HAL and theses.fr metadata; the thesis papers (ICASSP 2020, IEEE TCE 2021,
IEEE TCE 2022, PCS 2022) and later papers (DOIs in `content/phd.json`); Google Scholar; Hameed et al. (ISCA 2010),
Kuon & Rose (IEEE TCAD 2007).

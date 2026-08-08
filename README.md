# Cristian Mejia — Mechanical Engineering Portfolio

A single-page, technical-drawing-inspired portfolio for my ME work at
Stanford (B.S. Mechanical Engineering, minor in Aeronautics &
Astronautics, Class of 2029). Built as a lightweight static site:

- **HTML + CSS + vanilla JS** (no build step)
- **Three.js** from CDN for the interactive fighter-jet flight sim in the hero
- Monochrome warm-cream aesthetic: custom crosshair cursor, live UTC clock,
  boot-up sequence, registration marks, dimension callouts, and a drawing
  title-block footer.

## File map

```
index.html                  home page
projects/task-manager.html  project detail sheet (DWG CM-002)
projects/wind-turbine.html  project detail sheet (DWG CM-003)
styles.css                  shared theme + tokens (palette lives at the top)
project.css                 detail-sheet-only styles, loaded after styles.css
script.js                   shared chrome: cursor, clock, boot, scroll reveals
hero-jet.js                 the Three.js flight sim
assets/task-manager/        build photos
assets/wind-turbine/        build photos
```

`script.js` runs on every page and guards every element it touches, so a page
can omit the boot overlay or the clock without breaking. It pulls in
`hero-jet.js` with a dynamic `import()` only when the hero canvas is on the
page — so detail pages never download Three.js.

## Run locally

Because the page uses ES modules + an import map, open it through a
local web server (not by double-clicking the file).

```bash
cd portfolio
python3 -m http.server 8080
# open http://localhost:8080
```

```bash
# Node alternative (no install)
cd portfolio
npx --yes serve .
```

## Sections

1. **Hero** — 3D fighter-jet flight sim, intro, quick stats.
2. **Selected Work** — completed builds only. Both cards are clickable and
   open a detail sheet:
   - `01` Automated Task Management System _(built · independent)_ →
     `projects/task-manager.html`
   - `02` Small-Scale Wind Turbine _(built · CEE 34N)_ →
     `projects/wind-turbine.html`
3. **About** — personal background + interests.
4. **Education** — Stanford details and relevant coursework.
5. **Toolchain** — CAD, MATLAB, Python, 3D printing, etc.
6. **Contact** — email, LinkedIn, GitHub, resume.

## Adding a project

Each project is an `<article class="card">` inside `.work__grid` in
`index.html`. Copy the existing one and update the `<h3>`, `<p>`, and
`<li>` tags. Swap the inline `<svg class="cad …">` for an
`<img src="renders/yourProject.png">` once you have real renders or photos.

Status badges: `status--built` (finished, shows a filled square) or
`status--concept` (in progress / not built yet).

Projects currently use `card card--feature`, which spans the full grid width
and puts the drawing beside its details, alternating sides as they stack. This
suits a short, detailed list. **Once there are roughly four or more projects,
drop `card--feature`** so they flow into the normal 3-column grid instead.
Also bump the `NN DRAWINGS` count in the section divider.

The palette is at the top of `styles.css` as CSS variables — `--bg`,
`--ink` (warm cream), and `--ink-dim`.

## Cache busting — bump this when you edit CSS or JS

GitHub Pages serves assets with `max-age=600`, so a visitor can end up with
new HTML and a ten-minute-old stylesheet. That combination looks badly broken
rather than merely stale: hover-only elements show permanently, and inline
SVGs with no CSS balloon to their 300×150 default.

So `styles.css`, `project.css`, and `script.js` are linked with a `?v=N`
query. **After editing any of them, bump `N` in every page** (currently `v=5`):

```bash
rg -n '\?v=' *.html projects/*.html
```

`script.js` passes its own `?v=` through to `hero-jet.js` via `import.meta.url`,
so that one updates itself.

As a second line of defence, icon `<svg>`s carry `width`/`height` attributes so
they stay small even with no CSS at all. CSS still overrides them, so the
attributes only matter when something has gone wrong. Diagram SVGs (`.cad`,
`.chain`, `.ticks`, `.annot`) deliberately omit them — they scale to fit.

## Adding a detail sheet

Only cards that actually have a page get the clickable treatment, so a card
never promises a page that doesn't exist. To wire one up, add to the
`<article>`:

1. `card--linked` on the article's class list.
2. `<a class="card__link" href="projects/your-project.html" aria-label="…">`
   as the first child — it stretches over the whole card.
3. `<span class="card__peek">DWG CM-00N</span>` inside `.card__sheet`
   (appears on the drawing on hover).
4. `<span class="card__cta">Click for more info …</span>` at the end of
   `.card__meta` (the arrow that slides in on hover).

Then copy either existing sheet as a starting point. Both share the structure
`.proj` header → `.proj__intro` → `.log` (numbered `.phase` build stages) →
`.arch` (diagram) → `.stack` (three-column grid) → `.cadblock` → `.nextnav`.
The `.stack__grid`/`.sub` pair is generic enough to hold a bill of materials
(task manager) or findings and team credits (wind turbine).

If a plate shows something that **isn't my own work** — a reference design or
a photo taken from elsewhere — add `plate--ref` alongside `plate`. It switches
the frame to a dashed rule, desaturates the image until hover, and tints the
caption key, so it can't be skimmed as part of the build. Say so in the
caption too; the wind turbine sheet uses this for its reference rotor.

Photos go in `assets/<project>/`. Bake EXIF rotation into the pixels rather
than relying on the orientation flag, since the `.shot` frames use a fixed
`aspect-ratio`:

```bash
sips -s format jpeg -Z 1800 IMG_XXXX.HEIC --out out.jpg   # HEIC → JPEG
python3 -c "from PIL import Image,ImageOps; \
im=ImageOps.exif_transpose(Image.open('out.jpg')).convert('RGB'); \
im.thumbnail((1600,1600)); im.save('out.jpg',quality=84,optimize=True)"
```

When the source is a class presentation, pull the originals out of the exported
PDF instead of screenshotting slides — they come out at full resolution and
already correctly oriented:

```bash
python3 -c "import pymupdf; d=pymupdf.open('deck.pdf'); \
[pymupdf.Pixmap(d,x[0]).save(f'p{p+1}_{i}.png') \
for p in range(len(d)) for i,x in enumerate(d[p].get_images(full=True))]"
```

Build stages alternate sides automatically via `:nth-of-type(even)`. The
timeline rail is drawn with `.phase__rail::before`, whose negative `bottom`
value is tuned to `.phase`'s vertical padding — if you change that padding,
update the offset in `project.css` or the line will break between stages.

## Deploy

Static files — drop the `portfolio/` folder on GitHub Pages, Netlify,
Vercel, or Cloudflare Pages.

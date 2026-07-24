# Cristian Mejia — Mechanical Engineering Portfolio

A single-page, technical-drawing-inspired portfolio for my ME work at
Stanford (intended B.S. Mechanical Engineering, minor in Aeronautics &
Astronautics, Class of 2029). Built as a lightweight static site:

- **HTML + CSS + vanilla JS** (no build step)
- **Three.js** from CDN for the interactive fighter-jet flight sim in the hero
- Monochrome warm-cream aesthetic: custom crosshair cursor, live UTC clock,
  boot-up sequence, registration marks, dimension callouts, and a drawing
  title-block footer.

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
2. **Selected Work** — completed builds only:
   - `01` Small-Scale HAWT _(built · Wind Power class)_
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

The lone project currently uses `card card--feature`, which spans the full
grid and puts the drawing beside its details. **Once there are two or more
projects, drop `card--feature`** so they flow into the normal 3-column grid.
Also bump the `NN DRAWING(S)` count in the section divider.

The palette is at the top of `styles.css` as CSS variables — `--bg`,
`--ink` (warm cream), and `--ink-dim`.

## Deploy

Static files — drop the `portfolio/` folder on GitHub Pages, Netlify,
Vercel, or Cloudflare Pages.

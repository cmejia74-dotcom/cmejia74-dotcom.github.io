# Cristian Mejia — Mechanical Engineering Portfolio

A single-page, technical-drawing-inspired portfolio for my ME work at
Stanford (intended B.S. Mechanical Engineering, minor in Aeronautics &
Astronautics, Class of 2029). Built as a lightweight static site:

- **HTML + CSS + vanilla JS** (no build step)
- **Three.js** from CDN for the interactive 3D gear in the hero
- Blueprint aesthetic: custom crosshair cursor, live UTC clock, boot-up
  sequence, registration marks, dimension callouts, and a drawing
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

1. **Hero** — 3D rotating gear, intro, quick stats.
2. **Selected Work** — five personal concept sheets:
   - `01` Deployable Solar Array Hinge _(concept)_
   - `02` Star Tracker Optical Baffle _(concept)_
   - `03` Cold Gas Attitude Thruster Nozzle _(concept)_
   - `04` Reaction Wheel Assembly _(concept)_
   - `05` NACA 2412 Airfoil Study _(concept)_
3. **About** — personal background + interests.
4. **Education** — Stanford details, relevant coursework, awards.
5. **Toolchain** — CAD, MATLAB, Python, CubeSat subsystems, etc.
6. **Contact** — email + affiliations.

## Customize

When real projects land, each project is an `<article class="card">` in
`index.html`. Swap the inline `<svg class="cad …">` for an `<img src=
"renders/yourProject.png">`, update the `<h3>`, the `<p>`, the `<li>`
tags, and flip `status status--concept` to `status status--active` (or
remove the badge entirely).

The accent palette is at the top of `styles.css` as CSS variables:
`--accent` (amber) and `--accent-2` (blueprint cyan).

## Deploy

Static files — drop the `portfolio/` folder on GitHub Pages, Netlify,
Vercel, or Cloudflare Pages.

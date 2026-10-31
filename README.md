# Cristian Mejia — Mechanical Engineering Portfolio

Portfolio for my ME work at Stanford (B.S. Mechanical Engineering, intended minor
in Aeronautics and Astronautics, Class of 2029). It is laid out like a feature
spread in a botanical science journal: deep forest-green pages, near-white
type, one editorial serif, and white hairline technical drawings.

Plain HTML and CSS. No JavaScript, no build step for the pages themselves.

## File map

```
index.html                               home: hero, project features, about, contact
projects/task-manager.html               project article
projects/wind-turbine.html               project article
projects/motor-controller-enclosure.html project article
styles.css                               the whole design system (tokens at the top)
tools/build_figs.py                      generates the hairline SVG drawings
assets/task-manager/                     build photos
assets/wind-turbine/                     build photos
assets/motor-controller-enclosure/       Fusion 360 screenshots
assets/cristian-mejia-resume.pdf         résumé linked from Contact
```

## Run locally

```bash
cd portfolio
python3 -m http.server 8080
# open http://localhost:8080
```

## Design system

### Color

Every color has one job. Don't introduce new ones.

| Token              | Hex       | Use                                              |
| ------------------ | --------- | ------------------------------------------------ |
| `--moss`           | `#1B2F0A` | page background                                  |
| `--understory`     | `#0C1805` | footer and alternating bands (`.band`)           |
| `--leaf`           | `#424C26` | panels and image placeholders                    |
| `--vein`           | `#606A39` | hairline rules and drawing grids, **never text** |
| `--lotus`          | `#FAFCF5` | headlines, body text, all line art               |
| `--sage`           | `#A3AE96` | captions and secondary text, on Moss/Understory  |

### Type

Newsreader only, loaded from Google Fonts as a variable font. Optical size
is set explicitly with `font-variation-settings: "opsz" N` so it doesn't
drift with font size: 72 for display headlines, 16 for body, 12 for captions.
Headlines are sentence case with tight leading; body is 18px (17px on
phones) with prose capped at 64ch; captions and bylines are small italic in
Sage.

### Layout

A 12-column grid (`.grid`) inside `.wrap`, with wide side margins
(`--margin`). Text is left-aligned and ragged right. Figures run wider than
the text column and captions align to the figure's left edge. Projects are
separated by a single Vein hairline (`.rule`) — no cards.

Things deliberately absent: rounded corners, shadows, gradients, blur,
uppercase labels, scroll animations, icon fonts.

## Drawings

All line art is inline SVG in `currentColor` (Lotus), 1.1px strokes with no
fills, using `vector-effect: non-scaling-stroke` so hairlines stay hairlines
at any size. Stroke styles are classes in `styles.css`: `.cl` dash-dot
centerline, `.ph` phantom, `.hid` dashed hidden line, `.fl` dotted field
line, `.h` section hatching, `.grid` Vein grid.

The drawings are generated, not hand-edited. `tools/build_figs.py` builds each
one and injects it into every page between markers:

```html
<!-- FIG:generator -->
…generated SVG…
<!-- /FIG:generator -->
```

To change a drawing, edit its function in the script and re-run it:

```bash
python3 tools/build_figs.py
```

It is idempotent, so it's safe to run any time. Each SVG gets a `<title>`
and `<desc>` for screen readers.

**Labels on small screens.** Every leader ends in both a word label
(`.word`) and a single-letter key (`.key`). A container query swaps them
when the figure is narrower than 560px, and the caption's `.fig__key`
paragraph spells out the key. If you add a leader, add it to that caption
line too.

**Honesty.** Drawings are schematic and carry no invented dimensions —
dimension lines use words ("rotor diameter"), not numbers. Plate I on the
home page is a rendered texture, not a real micrograph, and its caption says
so. A photo that isn't our build (the reference drag rotor) says so in its
caption.

## Photos

Photos sit in a `<div class="photo">` inside their `<figure>` and are shown in
their original color.

Until a real image exists, use a `.placeholder` panel (Leaf, crossed by two
hairline diagonals) whose text names the file it is waiting for — copy the
one at the bottom of `projects/task-manager.html`. To fill it, swap the
whole `<div class="placeholder">` for
`<div class="photo"><img src="…" alt="…"></div>` and drop "Image to come"
from the caption.

Bake EXIF rotation into the pixels and keep files around 1600px:

```bash
sips -s format jpeg -Z 1800 IMG_XXXX.HEIC --out out.jpg   # HEIC → JPEG
python3 -c "from PIL import Image,ImageOps; \
im=ImageOps.exif_transpose(Image.open('out.jpg')).convert('RGB'); \
im.thumbnail((1600,1600)); im.save('out.jpg',quality=84,optimize=True)"
```

When the source is a class presentation, pull the originals out of the
exported PDF instead of screenshotting slides:

```bash
python3 -c "import pymupdf; d=pymupdf.open('deck.pdf'); \
[pymupdf.Pixmap(d,x[0]).save(f'p{p+1}_{i}.png') \
for p in range(len(d)) for i,x in enumerate(d[p].get_images(full=True))]"
```

## Adding a project

On the home page, copy one of the `<article class="feature …">` blocks.
`feature--a` puts text left with the photo right and the drawing running
wide underneath; `feature--b` mirrors it. Alternate them so the page doesn't
fall into a repeating pattern, and put an `<hr class="rule">` between
projects.

For the article page, copy either file in `projects/`. Sections are
`<section class="sec">` with a `.sec__head` (left three columns), a
`.sec__body` prose column, and optional `.sec__aside` (right margin figure),
`.sec__wide` or `.sec__half-l`/`.sec__half-r` figures. Wrap every other
section in `.band` for the Understory background.

## Cache busting

GitHub Pages caches assets for ten minutes, so `styles.css` is linked as
`styles.css?v=N`. **Bump `N` in every page after editing the CSS**
(currently `v=9`):

```bash
rg -n '\?v=' *.html projects/*.html
```

## Deploy

Static files. Pushing `main` publishes to GitHub Pages.

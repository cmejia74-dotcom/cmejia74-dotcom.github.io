"""Generate the hairline SVG figures and inject them into the portfolio pages
between <!-- FIG:name --> ... <!-- /FIG:name --> markers."""
import math, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [ROOT / "index.html", ROOT / "projects/task-manager.html", ROOT / "projects/wind-turbine.html",
         ROOT / "projects/motor-controller-enclosure.html"]


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Fig:
    def __init__(self, name, w, h, title, desc, label_size=None, key_size=None):
        self.name, self.w, self.h = name, w, h
        self.title, self.desc = title, desc
        self.ls = label_size or round(w / 50, 1)
        self.ks = key_size or round(w / 22, 1)
        self.defs, self.body = [], []
        self.n_clip = 0

    # primitives -----------------------------------------------------------
    def add(self, s):
        self.body.append(s)

    def line(self, x1, y1, x2, y2, cls=""):
        c = f' class="{cls}"' if cls else ""
        self.add(f'<line{c} x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')

    def path(self, d, cls="", extra=""):
        c = f' class="{cls}"' if cls else ""
        self.add(f'<path{c} d="{d}"{extra}/>')

    def circle(self, cx, cy, r, cls=""):
        c = f' class="{cls}"' if cls else ""
        self.add(f'<circle{c} cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>')

    def rect(self, x, y, w, h, cls="", rx=0):
        c = f' class="{cls}"' if cls else ""
        r = f' rx="{f(rx)}"' if rx else ""
        self.add(f'<rect{c} x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}/>')

    def text(self, x, y, s, anchor="start", cls="", size=None, rot=None):
        c = f' class="{cls}"' if cls else ""
        sz = f' font-size="{f(size or self.ls)}"'
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        t = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot is not None else ""
        self.add(f'<text{c} x="{f(x)}" y="{f(y)}"{a}{sz}{t}>{s}</text>')

    # drawing conventions ---------------------------------------------------
    def arrowhead(self, x, y, ang, L=9, spread=21):
        """Open chevron with its tip at (x,y), pointing along `ang` (radians)."""
        a1 = ang + math.pi - math.radians(spread)
        a2 = ang + math.pi + math.radians(spread)
        self.path(f"M{f(x + L*math.cos(a1))} {f(y + L*math.sin(a1))} L{f(x)} {f(y)} "
                  f"L{f(x + L*math.cos(a2))} {f(y + L*math.sin(a2))}")

    def arrow(self, x1, y1, x2, y2, cls=""):
        self.line(x1, y1, x2, y2, cls)
        self.arrowhead(x2, y2, math.atan2(y2 - y1, x2 - x1))

    def dim(self, p1, p2, off, label, word=True, gap=6, over=6, text_off=8, rot=None):
        """Linear dimension between feature points p1, p2, offset by vector `off`."""
        (x1, y1), (x2, y2) = p1, p2
        ox, oy = off
        n = math.hypot(ox, oy)
        ux, uy = ox / n, oy / n
        # extension lines: start a small gap off the feature, overshoot the dim line
        for (x, y) in (p1, p2):
            self.line(x + ux*gap, y + uy*gap, x + ox + ux*over, y + oy + uy*over)
        a, b = (x1 + ox, y1 + oy), (x2 + ox, y2 + oy)
        self.line(*a, *b)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        self.arrowhead(*b, ang)
        self.arrowhead(*a, ang + math.pi)
        if rot is None:
            rot_deg = math.degrees(ang)
            if rot_deg > 90 or rot_deg < -90:
                rot_deg += 180
            rot = rot_deg if abs(rot_deg) > 0.01 else None
        # baseline sits text_off "above" the dimension line in the text's own frame
        r = math.radians(rot or 0)
        upx, upy = math.sin(r), -math.cos(r)
        mx, my = (a[0] + b[0]) / 2 + upx*text_off, (a[1] + b[1]) / 2 + upy*text_off
        self.text(mx, my, label, "middle", rot=rot)

    def angle_dim(self, cx, cy, r, a1, a2, label, lr=None):
        """Angular dimension: arc from a1 to a2 (degrees, SVG convention)."""
        A1, A2 = math.radians(a1), math.radians(a2)
        p1 = (cx + r*math.cos(A1), cy + r*math.sin(A1))
        p2 = (cx + r*math.cos(A2), cy + r*math.sin(A2))
        large = 1 if abs(a2 - a1) > 180 else 0
        sweep = 1 if a2 > a1 else 0
        self.path(f"M{f(p1[0])} {f(p1[1])} A{f(r)} {f(r)} 0 {large} {sweep} {f(p2[0])} {f(p2[1])}")
        # tangents at the ends
        self.arrowhead(*p2, A2 + (math.pi/2 if sweep else -math.pi/2))
        self.arrowhead(*p1, A1 - (math.pi/2 if sweep else -math.pi/2))
        am = math.radians((a1 + a2) / 2)
        lr = lr or r + self.ls*1.2
        self.text(cx + lr*math.cos(am), cy + lr*math.sin(am) + self.ls*0.35, label, "middle")

    def centre(self, cx, cy, hl, vl=None):
        vl = hl if vl is None else vl
        self.line(cx - hl, cy, cx + hl, cy, "cl")
        self.line(cx, cy - vl, cx, cy + vl, "cl")

    def leader(self, pts, word, key, anchor="start", dot=True):
        """Leader from a feature (first point) to a label (last point)."""
        d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)
        self.path(d)
        if dot:
            self.circle(pts[0][0], pts[0][1], 2.2)
        x, y = pts[-1]
        dx = 7 if anchor == "start" else -7 if anchor == "end" else 0
        self.text(x + dx, y + self.ls*0.35, word, anchor, "word")
        self.text(x + dx, y + self.ks*0.36, key, anchor, "key", size=self.ks)

    def hatch(self, d, spacing=7, angle=45, bbox=None, rule="nonzero"):
        """Light hatching clipped to path `d` (a cut section)."""
        self.n_clip += 1
        cid = f"{self.name}-cut{self.n_clip}"
        self.defs.append(f'<clipPath id="{cid}"><path d="{d}" clip-rule="{rule}"/></clipPath>')
        x0, y0, x1, y1 = bbox or (0, 0, self.w, self.h)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R = math.hypot(x1 - x0, y1 - y0) / 2 + spacing
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)       # hatch direction
        nx, ny = -dy, dx                        # step direction
        lines = []
        k = -R
        while k <= R:
            px, py = cx + nx*k, cy + ny*k
            lines.append(f'<line x1="{f(px - dx*R)}" y1="{f(py - dy*R)}" x2="{f(px + dx*R)}" y2="{f(py + dy*R)}"/>')
            k += spacing
        self.add(f'<g class="h" clip-path="url(#{cid})">' + "".join(lines) + "</g>")
        self.path(d, extra=f' fill-rule="{rule}"' if rule != "nonzero" else "")

    def svg(self, extra_cls=""):
        tid, did = f"{self.name}-t", f"{self.name}-d"
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        cls = "fig-art" + (f" {extra_cls}" if extra_cls else "")
        return (f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="{tid} {did}" fill="none" stroke="currentColor" stroke-width="1.1">'
                f'<title id="{tid}">{self.title}</title><desc id="{did}">{self.desc}</desc>'
                f'{defs}{"".join(self.body)}</svg>')


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r*math.cos(a), cy + r*math.sin(a)


def poly(pts, close=True):
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + (" Z" if close else "")


def rotpts(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx)*c - (y - cy)*s, cy + (x - cx)*s + (y - cy)*c) for x, y in pts]


# ===========================================================================
# Generator cross-section — the hero figure
# ===========================================================================
def generator():
    g = Fig("gen", 900, 800,
            "Cross-section of the six-magnet generator",
            "Schematic cross-section drawn in white hairlines. A hatched circular PLA shaft sits at "
            "the center with six rectangular magnets arranged radially around it at 60 degree "
            "intervals, each hatched as a cut section. A dash-dot circle marks the path the magnet "
            "tips sweep. Dotted curves between neighboring magnets suggest the magnetic field. A "
            "square box wall, hatched, surrounds the rotor with an air gap; bundles of copper wire, "
            "drawn as rows of small circles, sit against the top and bottom walls. Centerlines cross "
            "at the shaft, an angular dimension marks 60 degrees between two magnets, and leader "
            "lines point to labels for the shaft, a magnet, the winding, the box wall, the rotation "
            "path and the air gap.", label_size=17)
    cx, cy = 450, 400
    # faint graph-paper grid in vein
    grid = []
    for x in range(30, 900, 40):
        grid.append(f'<line x1="{x}" y1="20" x2="{x}" y2="780"/>')
    for y in range(20, 800, 40):
        grid.append(f'<line x1="30" y1="{y}" x2="870" y2="{y}"/>')
    g.add('<g class="grid">' + "".join(grid) + "</g>")

    # box wall, sectioned (square ring)
    o, t = 228, 15
    outer = poly([(cx-o, cy-o), (cx+o, cy-o), (cx+o, cy+o), (cx-o, cy+o)])
    inner = poly([(cx-o+t, cy-o+t), (cx-o+t, cy+o-t), (cx+o-t, cy+o-t), (cx+o-t, cy-o+t)])
    g.hatch(outer + " " + inner, 7, 45, (cx-o, cy-o, cx+o, cy+o), rule="evenodd")

    # copper winding bundles against the top and bottom walls (wire cut ends)
    for side in (-1, 1):
        y0 = cy + side*(o + 4) - (36 if side < 0 else 0)
        g.rect(cx - 180, y0, 360, 36)
        for row in range(3):
            for col in range(30):
                g.circle(cx - 174 + 6 + col*11.6, y0 + 6.5 + row*11.5, 4.2)

    # rotation path
    rp = 138
    g.circle(cx, cy, rp, "cl")

    # field lines between neighboring magnets (schematic)
    for k in range(6):
        a1, a2 = -90 + k*60, -90 + (k+1)*60
        p1, p2 = pol(cx, cy, 120, a1 + 9), pol(cx, cy, 120, a2 - 9)
        c = pol(cx, cy, 178, (a1 + a2) / 2)
        g.path(f"M{f(p1[0])} {f(p1[1])} Q{f(c[0])} {f(c[1])} {f(p2[0])} {f(p2[1])}", "fl")
        p1, p2 = pol(cx, cy, 104, a1 + 12), pol(cx, cy, 104, a2 - 12)
        c = pol(cx, cy, 140, (a1 + a2) / 2)
        g.path(f"M{f(p1[0])} {f(p1[1])} Q{f(c[0])} {f(c[1])} {f(p2[0])} {f(p2[1])}", "fl")

    # six magnets, sectioned, hatched the other way to read as another material
    for k in range(6):
        ang = -90 + k*60
        hw, r0, r1 = 17, 34, 120
        pts = [(r0, -hw), (r1, -hw), (r1, hw), (r0, hw)]
        a = math.radians(ang)
        P = [(cx + x*math.cos(a) - y*math.sin(a), cy + x*math.sin(a) + y*math.cos(a)) for x, y in pts]
        xs, ys = [p[0] for p in P], [p[1] for p in P]
        g.hatch(poly(P), 6, -45, (min(xs), min(ys), max(xs), max(ys)))

    # shaft, sectioned
    rs = 26
    d = (f"M{cx-rs} {cy} A{rs} {rs} 0 1 0 {cx+rs} {cy} A{rs} {rs} 0 1 0 {cx-rs} {cy} Z")
    g.hatch(d, 5, 45, (cx-rs, cy-rs, cx+rs, cy+rs))

    # centerlines
    g.centre(cx, cy, 292, 292)
    # magnet centerlines for the angular dimension
    for ang in (-90, -30):
        p1, p2 = pol(cx, cy, 124, ang), pol(cx, cy, 206, ang)
        g.line(*p1, *p2, "cl")
    g.angle_dim(cx, cy, 196, -90, -30, "60°", lr=214)

    # rotation arrow
    a1, a2 = 112, 152
    p1, p2 = pol(cx, cy, 160, a1), pol(cx, cy, 160, a2)
    g.path(f"M{f(p1[0])} {f(p1[1])} A160 160 0 0 1 {f(p2[0])} {f(p2[1])}")
    g.arrowhead(*p2, math.radians(a2) + math.pi/2)

    # air gap dimension (radial, lower right)
    a = math.radians(38)
    ri = (o - t) / math.cos(a) if abs(math.cos(a)) > abs(math.sin(a)) else (o - t) / abs(math.sin(a))
    q1, q2 = pol(cx, cy, rp, 38), pol(cx, cy, ri, 38)
    g.line(*q1, *q2)
    g.arrowhead(*q1, a + math.pi)
    g.arrowhead(*q2, a)

    # leaders and labels
    g.leader([pol(cx, cy, 14, 18), pol(cx, cy, 90, 2), (700, 400 + 26), (708, 426)], "PLA shaft, sectioned", "a")
    g.leader([pol(cx, cy, 96, -26), (700, 268)], "magnet, one of six", "b")
    g.leader([(cx - 150, cy - o - 22), (300, 120), (200, 120)], "copper winding, sectioned", "c", "end")
    g.leader([(cx - o + 7, cy + 150), (200, 610)], "box wall, sectioned", "d", "end")
    g.leader([pol(cx, cy, rp, 196), (200, 330)], "rotation path", "e", "end")
    mid = pol(cx, cy, (rp + ri) / 2, 38)
    g.leader([mid, (700, 560)], "air gap", "f")
    return g.svg()


# ===========================================================================
# Enclosure section
# ===========================================================================
def enclosure():
    e = Fig("encl", 960, 600,
            "Section through the hinged enclosure",
            "Schematic section drawn in white hairlines. An open-topped base with hatched walls and "
            "floor sits on a ground line. Inside are a breadboard with the ESP32 board on it, an "
            "18650 cell on its charge shield, and the INMP441 microphone against the left wall with "
            "small arcs showing sound arriving from outside. A hinge pin at the back right carries "
            "the lid, drawn hatched and swung partly open, with the display and touch panel set "
            "into it; a dashed phantom outline shows the lid closed. An arc with an arrowhead "
            "shows the lid swing. Dimension lines give the overall width and the interior depth, "
            "and leader lines point to labels for each part.", label_size=17)
    # ground
    e.line(150, 472, 820, 472)
    for x in range(156, 820, 14):
        e.line(x, 472, x - 9, 481)
    # base, sectioned U
    U = poly([(200, 300), (212, 300), (212, 458), (748, 458), (748, 300), (760, 300), (760, 470), (200, 470)])
    e.hatch(U, 7, 45, (200, 300, 760, 470))
    # breadboard with hole rows
    e.rect(244, 434, 290, 24)
    e.line(250, 442, 528, 442, "hid")
    e.line(250, 450, 528, 450, "hid")
    # ESP32 board + pin headers + USB port
    e.rect(292, 419, 150, 15)
    for x in range(298, 440, 9):
        e.line(x, 434, x, 438)
    e.rect(282, 423, 10, 8)
    # charge shield + cell
    e.rect(566, 447, 160, 11)
    e.rect(578, 413, 136, 34, rx=14)
    e.line(704, 413, 704, 447)
    # microphone board on left wall + sound arcs outside
    e.rect(212, 362, 13, 34)
    for r in (16, 28, 40):
        e.path(f"M{200 - r*0.55} {379 - r*0.8} A{r} {r} 0 0 0 {200 - r*0.55} {379 + r*0.8}")
    # wiring (gentle curves)
    e.path("M330 419 C 318 392, 262 390, 225 382")
    e.path("M430 419 C 470 380, 560 396, 592 413")
    e.path("M420 419 C 430 340, 640 330, 742 312")
    # hinge pin
    hx, hy = 754, 294
    e.circle(hx, hy, 7)
    e.centre(hx, hy, 14)
    # lid, closed (phantom)
    e.rect(200, 288, 554, 12, "ph")
    # lid, open: rotate about the hinge
    ang = 26
    seg1 = rotpts([(200, 288), (290, 288), (290, 300), (200, 300)], hx, hy, ang)
    seg2 = rotpts([(600, 288), (748, 288), (748, 300), (600, 300)], hx, hy, ang)
    allp = seg1 + seg2
    bb = (min(p[0] for p in allp) - 4, min(p[1] for p in allp) - 4, max(p[0] for p in allp) + 4, max(p[1] for p in allp) + 4)
    e.hatch(poly(seg1), 7, 45, bb)
    e.hatch(poly(seg2), 7, 45, bb)
    disp = rotpts([(290, 286), (600, 286), (600, 300), (290, 300)], hx, hy, ang)
    e.path(poly(disp))
    glass = rotpts([(296, 290), (594, 290)], hx, hy, ang)
    e.line(*glass[0], *glass[1])
    pcb = rotpts([(310, 300), (580, 300), (580, 308), (310, 308)], hx, hy, ang)
    e.path(poly(pcb))
    # swing arc
    r = 600
    p1 = (hx - r, hy)
    a2 = math.radians(180 + ang)  # direction of open lid from hinge (screen coords, y down)
    p2 = (hx + r*math.cos(a2), hy + r*math.sin(a2))
    e.path(f"M{f(p1[0])} {f(p1[1])} A{r} {r} 0 0 1 {f(p2[0])} {f(p2[1])}", "cl")
    e.arrowhead(*p2, a2 + math.pi/2)
    e.text(118, 214, "lid swing", "end", "word")
    # dimensions
    e.dim((200, 470), (760, 470), (0, 52), "overall width")
    e.dim((760, 300), (760, 458), (66, 0), "interior depth", rot=90)
    # leaders
    mid_disp = rotpts([(445, 288)], hx, hy, ang)[0]
    e.leader([mid_disp, (530, 86), (570, 86)], "display and touch panel", "a")
    e.leader([(hx + 5, hy - 5), (800, 232), (840, 232)], "hinge pin", "b")
    e.leader([(232, 288), (168, 262), (150, 262)], "lid, closed", "c", "end")
    e.leader([(218, 370), (240, 340), (300, 340)], "INMP441 microphone", "d")
    e.leader([(360, 427), (340, 560), (300, 560)], "ESP32 on breadboard", "e", "end")
    e.leader([(646, 430), (660, 560), (700, 560)], "18650 cell on charge shield", "f")
    return e.svg()


# ===========================================================================
# Turbine side elevation
# ===========================================================================
def elevation():
    t = Fig("elev", 720, 900,
            "Side elevation of the wind turbine",
            "Schematic side view drawn in white hairlines. Wind arrows come from the left toward a "
            "printed nose-cone hub; two paper sails are seen edge-on above and below it with a "
            "vertical dimension for the rotor diameter. A horizontal dash-dot centerline marks the "
            "shaft, which runs back into the generator box, drawn with vertical lines for the "
            "copper winding, sitting on a platform at the top of a PVC tower. The shaft continues "
            "out the back as a spool with cord wound on it; a string hangs down to a cup, with a "
            "small arrow showing that the cup rises. An LED hangs off the front of the platform. "
            "The tower stands in a weighted base on a hatched ground line, and a second dimension "
            "gives the hub height.", label_size=17)
    axis = 212
    # ground
    t.line(220, 840, 600, 840)
    for x in range(226, 600, 14):
        t.line(x, 840, x - 9, 849)
    # weighted base
    t.path(poly([(306, 740), (454, 740), (446, 840), (314, 840)]))
    t.line(306, 756, 454, 756)
    # tower (PVC)
    t.line(370, 262, 370, 740)
    t.line(390, 262, 390, 740)
    t.line(380, 236, 380, 856, "cl")
    for y in (430, 438):
        t.line(370, y, 390, y)  # pipe coupling
    # platform
    t.rect(330, 250, 196, 12)
    # generator box with winding lines
    t.rect(392, 176, 112, 74)
    for x in range(404, 494, 5):
        t.line(x, 176, x, 250)
    # axis centerline
    t.line(56, axis, 662, axis, "cl")
    # shaft: hub to generator, and out the back as the spool
    t.line(232, axis - 5, 392, axis - 5)
    t.line(232, axis + 5, 392, axis + 5)
    t.line(504, axis - 4, 620, axis - 4)
    t.line(504, axis + 4, 620, axis + 4)
    t.line(620, axis - 4, 620, axis + 4)
    # cord wound on the spool
    for x in range(548, 592, 4):
        t.path(f"M{x} {axis - 9} C {x + 3} {axis - 3}, {x + 3} {axis + 3}, {x} {axis + 9}")
    # string and cup
    t.line(588, axis + 9, 588, 586)
    t.path(poly([(562, 586), (614, 586), (606, 642), (570, 642)]))
    t.line(566, 600, 610, 600)
    t.arrow(622, 520, 622, 470)
    t.text(632, 500, "rises", "start", "word")
    # hub (printed nose cone) and back plate
    t.path(f"M236 178 C 196 178, 166 196, 166 {axis} C 166 228, 196 246, 236 246")
    t.line(236, 178, 236, 246)
    # sails edge-on, upper and lower, with dowel spokes
    t.path(poly([(240, 186), (254, 186), (270, 28), (234, 22)]))
    t.line(247, 186, 252, 26)
    t.path(poly([(240, 238), (254, 238), (270, 396), (234, 402)]))
    t.line(247, 238, 252, 398)
    # LED on the platform's front edge
    t.line(392, 240, 352, 266)
    t.line(392, 244, 358, 270)
    t.circle(348, 282, 9)
    t.path("M341 290 L341 300 M355 290 L355 300")
    # wind
    for y in (120, 212, 304):
        t.arrow(30, y, 118, y)
    t.text(30, 100, "wind", "start", "word")
    # dimensions
    t.dim((234, 22), (234, 402), (-70, 0), "rotor diameter", rot=-90)
    t.line(600, 840, 680, 840)
    t.line(664, 212, 680, 212)
    t.line(674, 218, 674, 834)
    t.arrowhead(674, 218, -math.pi/2)
    t.arrowhead(674, 834, math.pi/2)
    t.text(690, 526, "hub height", "middle", "word", rot=90)
    # leaders
    t.leader([(198, 192), (150, 58), (110, 58)], "printed hub", "a", "end")
    t.leader([(262, 96), (300, 72), (330, 72)], "paper sail, edge-on", "b")
    t.leader([(470, 182), (520, 128), (560, 128)], "generator and winding", "c")
    t.leader([(572, axis - 8), (600, 168), (628, 168)], "spool", "d")
    t.leader([(572, 630), (540, 690), (520, 690)], "string and cup", "e", "end")
    t.leader([(356, 290), (420, 330), (440, 330)], "LED", "f")
    t.leader([(370, 600), (320, 620), (290, 620)], "PVC tower", "g", "end")
    t.leader([(310, 790), (260, 790), (240, 790)], "weighted base", "h", "end")
    return t.svg()


# ===========================================================================
# Solidity comparison
# ===========================================================================
def solidity():
    s = Fig("sol", 960, 470,
            "Two rotors over the same swept disc",
            "Two schematic front views side by side, each inside a dash-dot circle marking the swept "
            "disc, with centerlines crossing at the hub. Left, labelled a: three thin tapered airfoil "
            "blades leave most of the disc open. Right, labelled b: wide paper sails on dowel spokes "
            "cover much more of it.", label_size=16)
    R = 180
    for (cx, tag) in ((250, "a"), (710, "b")):
        cy = 236
        s.circle(cx, cy, R, "cl")
        s.centre(cx, cy, R + 22)
        s.text(cx - R - 10, cy - R - 2, f"({tag})", "start", "up", size=24)
    # (a) airfoil blades
    cx, cy = 250, 236
    for k in range(3):
        ang = k*120
        blade = "M -9 -17 C -13 -80, -8 -140, -3 -176 L 3 -176 C 7 -140, 11 -80, 9 -17 Z"
        s.path(blade, extra=f' transform="translate({cx} {cy}) rotate({ang})"')
    s.circle(cx, cy, 17)
    # (b) drag sails
    cx = 710
    for k in range(6):
        ang = k*60
        sail = "M -6 -21 L -50 -168 Q 0 -183 50 -168 L 6 -21 Z"
        s.path(sail, extra=f' transform="translate({cx} {cy}) rotate({ang})"')
        s.path("M 0 -21 L 0 -176", extra=f' transform="translate({cx} {cy}) rotate({ang})"')
    s.circle(cx, cy, 21)
    # labels
    s.leader([pol(250, 236, R, -38), (468, 70)], "swept disc", "")
    s.leader([pol(250, 236, 120, 120 + 90 - 4), (40, 420)], "thin airfoil blade", "", "start")
    s.leader([pol(710, 236, 120, 60 - 90 + 9), (930, 60)], "paper sail", "", "end")
    return s.svg()


# ===========================================================================
# Flow diagrams (vertical so they hold up on phones)
# ===========================================================================
def box(g, x, y, w, h, label, sub=None):
    g.rect(x, y, w, h)
    if sub:
        g.text(x + w/2, y + h/2 - 3, label, "middle", "up", size=21)
        g.text(x + w/2, y + h/2 + 20, sub, "middle", size=17)
    else:
        g.text(x + w/2, y + h/2 + 7, label, "middle", "up", size=21)


def power():
    p = Fig("pow", 520, 720,
            "Power path from wind to the two outputs",
            "Flow diagram in white hairlines. Wind pushes the paper sails, which turn the hub and "
            "rotor, which turn one shaft. The path then forks: on the left, six magnets sweep past "
            "copper coils and the LED lights, which needs RPM; on the right, a spool winds the "
            "string and the cup rises, which needs torque.", label_size=17)
    W, H = 250, 58
    x = (520 - W) / 2
    p.text(260, 34, "wind", "middle", size=17)
    p.arrow(260, 44, 260, 76)
    box(p, x, 80, W, H, "Paper sails")
    p.arrow(260, 80 + H, 260, 186)
    box(p, x, 190, W, H, "Hub and rotor")
    p.arrow(260, 190 + H, 260, 296)
    box(p, x, 300, W, H, "One shaft")
    # fork
    p.line(260, 300 + H, 260, 392)
    p.line(118, 392, 402, 392)
    p.arrow(118, 392, 118, 436)
    p.arrow(402, 392, 402, 436)
    bw = 214
    box(p, 118 - bw/2, 440, bw, 70, "Six magnets", "past copper coils")
    box(p, 402 - bw/2, 440, bw, 70, "Spool", "winds the string")
    p.arrow(118, 510, 118, 566)
    p.arrow(402, 510, 402, 566)
    p.text(118, 594, "the LED lights", "middle", size=21)
    p.text(402, 594, "the cup rises", "middle", size=21)
    p.text(118, 624, "needs RPM", "middle", size=17)
    p.text(402, 624, "needs torque", "middle", size=17)
    p.path("M20 418 L20 650 L238 650 L238 418", "ph")
    p.path("M282 418 L282 650 L500 650 L500 418", "ph")
    p.text(24, 680, "electrical", "start", size=17)
    p.text(496, 680, "mechanical", "end", size=17)
    return p.svg()


def signal():
    s = Fig("sig", 520, 700,
            "Signal path from microphone to screen",
            "Flow diagram in white hairlines with two dashed groups: the device on the left and a "
            "laptop server on the right. On the device, the INMP441 microphone sends I2S audio at "
            "16 kHz down to the ESP32. The ESP32 sends the audio over Wi-Fi to a FastAPI server, "
            "which passes it down to Whisper for transcription, then the transcript down to a "
            "language model. The extracted task goes back over Wi-Fi to the ESP32, which draws it "
            "on the ILI9341 display over SPI.")
    W, H = 200, 70
    lx, rx = 30, 290
    rows = [110, 300, 490]
    s.path(f"M{lx-14} 70 L{lx-14} 590 L{lx+W+14} 590 L{lx+W+14} 70 Z", "ph")
    s.path(f"M{rx-14} 70 L{rx-14} 590 L{rx+W+14} 590 L{rx+W+14} 70 Z", "ph")
    s.text(lx - 14, 54, "on the device", "start", size=17)
    s.text(rx + W + 14, 54, "on the laptop", "end", size=17)
    box(s, lx, rows[0], W, H, "INMP441", "microphone")
    box(s, lx, rows[1], W, H, "ESP32", "buffers and sends")
    box(s, lx, rows[2], W, H, "ILI9341", "display and touch")
    box(s, rx, rows[0], W, H, "FastAPI", "server")
    box(s, rx, rows[1], W, H, "Whisper", "speech to text")
    box(s, rx, rows[2], W, H, "Language model", "finds the task")
    cxl, cxr = lx + W/2, rx + W/2
    s.arrow(cxl, rows[0] + H, cxl, rows[1] - 4)
    s.text(cxl + 8, (rows[0] + H + rows[1]) / 2 + 5, "I2S, 16 kHz", size=17)
    s.arrow(cxl, rows[1] + H, cxl, rows[2] - 4)
    s.text(cxl + 8, (rows[1] + H + rows[2]) / 2 + 5, "SPI", size=17)
    s.arrow(cxr, rows[0] + H, cxr, rows[1] - 4)
    s.text(cxr + 8, (rows[0] + H + rows[1]) / 2 + 5, "audio", size=17)
    s.arrow(cxr, rows[1] + H, cxr, rows[2] - 4)
    s.text(cxr + 8, (rows[1] + H + rows[2]) / 2 + 5, "transcript", size=17)
    # ESP32 -> FastAPI (up and across), LLM -> ESP32 (back across)
    s.path(f"M{lx+W} {rows[1]+22} L260 {rows[1]+22} L260 {rows[0]+35}", "")
    s.arrow(260, rows[0] + 35, rx - 4, rows[0] + 35)
    s.path(f"M{rx} {rows[2]+35} L260 {rows[2]+35} L260 {rows[1]+50}")
    s.arrow(260, rows[1] + 50, lx + W + 4, rows[1] + 50)
    s.text(260, 640, "audio out and the task back, both over Wi-Fi", "middle", size=17)
    return s.svg()


# ===========================================================================
# Motor controller enclosure: the connector wall, seen from outside
# ===========================================================================
def connector_wall():
    c = Fig("cwall", 960, 330,
            "Connector wall of the enclosure, seen from outside",
            "Front view drawn in white hairlines of the long wall that faces down when the "
            "enclosure is installed. Phantom outlines show the motor controller’s connectors "
            "projected onto the wall: five round connectors, one wide rectangular connector and "
            "two small rectangular ones. Each is surrounded by a solid outline, the cutout, offset "
            "outward for clearance. Two small round holes sit between them. Centerlines cross each "
            "round connector, an arrow beside the wall points down, and leader lines label a "
            "connector outline and a cutout.", label_size=17)
    k = 860 / 914                           # traced from the Fusion 360 connector-face view
    X = lambda px: 40 + (px - 62) * k
    Y = lambda py: 70 + (py - 88) * k
    e = 4                                   # 0.5 mm offset, drawn larger than true scale
    c.rect(X(62), Y(88), X(976) - X(62), Y(212) - Y(88))
    for px, py, r in [(228, 140, 27), (556, 140, 27), (703, 140, 27), (812, 140, 27), (885, 140, 27)]:
        cx, cy, rr = X(px), Y(py), r * k
        c.circle(cx, cy, rr, "ph")
        c.circle(cx, cy, rr + e)
        c.centre(cx, cy, rr + e + 8)
    for px, py, r in [(289, 145, 10), (435, 145, 10)]:
        c.circle(X(px), Y(py), r * k)
    for x0, y0, x1, y1 in [(317, 117, 409, 148), (300, 168, 351, 198), (375, 168, 424, 198)]:
        c.rect(X(x0), Y(y0), X(x1) - X(x0), Y(y1) - Y(y0), "ph")
        c.rect(X(x0) - e, Y(y0) - e, X(x1) - X(x0) + 2*e, Y(y1) - Y(y0) + 2*e)
    # installed orientation
    c.arrow(934, 92, 934, 160)
    c.text(934, 190, "down", "middle", "word")
    # leaders
    r0 = 27 * k
    c.leader([(X(556), Y(140) + r0), (X(556) + 24, 254), (X(556) + 44, 254)],
             "connector outline, projected from the controller", "a")
    c.leader([(X(228), Y(140) + r0 + e), (X(228) + 20, 296), (X(228) + 40, 296)],
             "cutout, offset 0.5 mm all round", "b")
    return c.svg()


# ===========================================================================
# Micrograph plate — feTurbulence with a hard threshold
# ===========================================================================
def micrograph():
    w, h = 600, 450
    return (
        f'<svg class="fig-art" viewBox="0 0 {w} {h}" role="img" aria-labelledby="micro-t micro-d">'
        '<title id="micro-t">Rendered micrograph texture</title>'
        '<desc id="micro-d">A high-contrast black-and-white organic texture: a network of thin, '
        'irregular white walls enclosing dark cells of varying size, slightly stretched in one '
        'direction. A small scale bar sits in the lower right corner.</desc>'
        '<defs><filter id="micro" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.014 0.026" numOctaves="4" seed="11" result="n"/>'
        '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0.98  0 0 0 0 0.988  0 0 0 0 0.961  1 0 0 0 0"/>'
        '<feComponentTransfer><feFuncA type="discrete" '
        'tableValues="0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0"/></feComponentTransfer>'
        '</filter></defs>'
        f'<rect width="{w}" height="{h}" fill="#0C1805"/>'
        f'<rect width="{w}" height="{h}" filter="url(#micro)"/>'
        f'<rect x="{w-176}" y="{h-48}" width="158" height="34" fill="#0C1805"/>'
        f'<g fill="none" stroke="#FAFCF5" stroke-width="1.25">'
        f'<line x1="{w-162}" y1="{h-26}" x2="{w-92}" y2="{h-26}" vector-effect="non-scaling-stroke"/>'
        f'<line x1="{w-162}" y1="{h-31}" x2="{w-162}" y2="{h-21}" vector-effect="non-scaling-stroke"/>'
        f'<line x1="{w-92}" y1="{h-31}" x2="{w-92}" y2="{h-21}" vector-effect="non-scaling-stroke"/></g>'
        f'<text x="{w-28}" y="{h-21}" font-size="15" font-style="italic" text-anchor="end" fill="#FAFCF5">100 µm</text>'
        '</svg>'
    )


FIGS = {
    "generator": generator,
    "enclosure": enclosure,
    "elevation": elevation,
    "solidity": solidity,
    "power": power,
    "signal": signal,
    "micrograph": micrograph,
    "connector_wall": connector_wall,
}

if __name__ == "__main__":
    built = {k: fn() for k, fn in FIGS.items()}
    for page in PAGES:
        html = page.read_text()
        n = 0
        for name, svg in built.items():
            pat = re.compile(rf"(<!-- FIG:{name} -->)(.*?)(<!-- /FIG:{name} -->)", re.S)
            html, c = pat.subn(lambda m: f"{m.group(1)}\n{svg}\n{m.group(3)}", html)
            n += c
        page.write_text(html)
        print(f"{page.relative_to(ROOT)}: {n} figures injected")

"""Inline SVG figures for the notes, computed rather than eyeballed.

Usage:
    cp SKILL_DIR/assets/figs.py SCRATCHPAD/figs.py
    # add one generator per figure below the marker, e.g.  def f_eps_band(): ... return svg(...)
    python3 -I figs.py src.html OUTDIR/name.html

Every `{{FIG:eps-band}}` placeholder in src.html is replaced by the SVG that
`f_eps_band()` returns (hyphens in the placeholder map to underscores in the
function name). The script fails if a placeholder has no generator. It also
wraps inline maths that is followed by punctuation in <span class="nw"> so a
comma or period never starts a line of its own; the template defines .nw.

Panel maps mathematical coordinates to pixels. One SVG can hold several panels
side by side (pass ox= offsets). Conventions: thin black strokes, one accent
colour (ACC) for the key object, panel titles via title= (never a label
floating inside the plot), labels in plain Unicode (ε, x², ≤) because KaTeX
does not typeset inside SVG, and all curves computed from the function.
"""
import math, re, sys

ACC = "#2b5aa8"   # accent colour: bands, highlighted arcs, squeezed curves
PI = math.pi


def fmt(v):
    return f"{v:.1f}"


def gl(v):
    """Tick label: integers without .0, proper minus sign."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).replace("-", "−")


class Panel:
    def __init__(self, w, h, xr, yr, ox=0, oy=0, pad=(18, 12, 20, 14), title=None):
        # w, h: pixel size of this panel; xr, yr: (min, max) in maths coordinates
        # pad = left, right, bottom, top (pixels); ox, oy: offset inside the SVG
        if title:
            pad = (pad[0], pad[1], pad[2], max(pad[3], 28))
        self.w, self.h = w, h
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.ox, self.oy = ox, oy
        self.pl, self.pr, self.pb, self.pt = pad
        self.out = []
        if title:
            self.out.append(f'<text x="{fmt(ox + w / 2)}" y="{fmt(oy + 12)}" text-anchor="middle" font-size="12">{title}</text>')

    # coordinate maps
    def X(self, x):
        return self.ox + self.pl + (x - self.x0) / (self.x1 - self.x0) * (self.w - self.pl - self.pr)

    def Y(self, y):
        return self.oy + self.h - self.pb - (y - self.y0) / (self.y1 - self.y0) * (self.h - self.pb - self.pt)

    def axes(self, xticks=(), yticks=(), ax=0.0, ay=0.0, frame=False, xname="x", yname="y"):
        """Axes through (ax, ay) with arrowheads; frame=True puts them at the panel's lower-left.
        Ticks are values or (value, label) pairs."""
        o = self.out
        yaxis_x = self.x0 if frame else ax
        xaxis_y = self.y0 if frame else ay
        X0, X1 = self.X(self.x0), self.X(self.x1)
        Y0, Y1 = self.Y(self.y0), self.Y(self.y1)
        o.append(f'<line x1="{fmt(X0)}" y1="{fmt(self.Y(xaxis_y))}" x2="{fmt(X1)}" y2="{fmt(self.Y(xaxis_y))}" stroke="#000" stroke-width="0.8" marker-end="url(#ar)"/>')
        o.append(f'<line x1="{fmt(self.X(yaxis_x))}" y1="{fmt(Y0)}" x2="{fmt(self.X(yaxis_x))}" y2="{fmt(Y1)}" stroke="#000" stroke-width="0.8" marker-end="url(#ar)"/>')
        if xname:
            o.append(f'<text x="{fmt(X1+2)}" y="{fmt(self.Y(xaxis_y)+4)}" font-style="italic">{xname}</text>')
        if yname:
            o.append(f'<text x="{fmt(self.X(yaxis_x)+4)}" y="{fmt(Y1+4)}" font-style="italic">{yname}</text>')
        for t in xticks:
            v, lab = (t if isinstance(t, tuple) else (t, gl(t)))
            o.append(f'<line x1="{fmt(self.X(v))}" y1="{fmt(self.Y(xaxis_y)-3)}" x2="{fmt(self.X(v))}" y2="{fmt(self.Y(xaxis_y)+3)}" stroke="#000" stroke-width="0.8"/>')
            o.append(f'<text x="{fmt(self.X(v))}" y="{fmt(self.Y(xaxis_y)+15)}" text-anchor="middle" font-size="11">{lab}</text>')
        for t in yticks:
            v, lab = (t if isinstance(t, tuple) else (t, gl(t)))
            o.append(f'<line x1="{fmt(self.X(yaxis_x)-3)}" y1="{fmt(self.Y(v))}" x2="{fmt(self.X(yaxis_x)+3)}" y2="{fmt(self.Y(v))}" stroke="#000" stroke-width="0.8"/>')
            o.append(f'<text x="{fmt(self.X(yaxis_x)-6)}" y="{fmt(self.Y(v)+4)}" text-anchor="end" font-size="11">{lab}</text>')

    def curve(self, f, a, b, n=400, color="#000", width=1.4, dash=None, xs=None):
        """Plot y=f(x) on [a,b] from n+1 computed points (or the given xs), clipping at the
        panel's vertical range so poles become separate branches that never cross the edge."""
        ys_lo, ys_hi = self.y0 - 0.02 * (self.y1 - self.y0), self.y1 + 0.02 * (self.y1 - self.y0)
        if xs is None:
            xs = [a + (b - a) * i / n for i in range(n + 1)]
        segs, cur, prev = [], [], None
        for x in xs:
            try:
                y = f(x)
            except (ZeroDivisionError, ValueError, OverflowError):
                y = None
            if y is None or not math.isfinite(y):
                if cur: segs.append(cur); cur = []
                prev = None
                continue
            if ys_lo <= y <= ys_hi:
                if not cur and prev is not None:
                    px, py = prev
                    yb = ys_hi if py > ys_hi else ys_lo
                    if py != y:
                        t = (yb - py) / (y - py)
                        cur.append((px + t * (x - px), yb))
                cur.append((x, y))
            else:
                if cur:
                    px, py = cur[-1]
                    yb = ys_hi if y > ys_hi else ys_lo
                    t = (yb - py) / (y - py)
                    cur.append((px + t * (x - px), yb))
                    segs.append(cur); cur = []
            prev = (x, y)
        if cur: segs.append(cur)
        d = " ".join("M" + " L".join(f"{fmt(self.X(x))},{fmt(self.Y(y))}" for x, y in s) for s in segs if len(s) > 1)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} stroke-linejoin="round"/>')

    def line(self, x1, y1, x2, y2, color="#000", width=1.0, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<line x1="{fmt(self.X(x1))}" y1="{fmt(self.Y(y1))}" x2="{fmt(self.X(x2))}" y2="{fmt(self.Y(y2))}" stroke="{color}" stroke-width="{width}"{da}/>')

    def vasym(self, x):
        self.line(x, self.y0, x, self.y1, color="#666", width=0.9, dash="4 3")

    def hasym(self, y):
        self.line(self.x0, y, self.x1, y, color="#666", width=0.9, dash="4 3")

    def dot(self, x, y, open_=False, r=3.0, color="#000"):
        fill = "#fff" if open_ else color
        self.out.append(f'<circle cx="{fmt(self.X(x))}" cy="{fmt(self.Y(y))}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="1.1"/>')

    def text(self, x, y, s, anchor="start", dx=0, dy=0, size=None, color="#000", italic=False):
        """Label at maths coordinates (x, y) with a pixel nudge (dx, dy). Escape < as &lt;."""
        sz = f' font-size="{size}"' if size else ""
        it = ' font-style="italic"' if italic else ""
        self.out.append(f'<text x="{fmt(self.X(x)+dx)}" y="{fmt(self.Y(y)+dy)}" text-anchor="{anchor}"{sz}{it} fill="{color}">{s}</text>')

    def rect(self, x0, y0, x1, y1, fill=ACC, op=0.15, stroke=None, dash=None):
        """Shaded band/region between maths coordinates (x0,y0) and (x1,y1)."""
        X0, X1 = sorted((self.X(x0), self.X(x1)))
        Y0, Y1 = sorted((self.Y(y0), self.Y(y1)))
        st = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.out.append(f'<rect x="{fmt(X0)}" y="{fmt(Y0)}" width="{fmt(X1-X0)}" height="{fmt(Y1-Y0)}" fill="{fill}" fill-opacity="{op}"{st}{da}/>')

    def arc(self, r, t0, t1, color=ACC, width=2.6, n=100, fill=None):
        """Circular arc about the origin from angle t0 to t1 (radians); fill=... gives a sector."""
        ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
        pts = " ".join(f"L{fmt(self.X(r * math.cos(s)))},{fmt(self.Y(r * math.sin(s)))}" for s in ts)
        if fill:
            d = f"M{fmt(self.X(0))},{fmt(self.Y(0))} {pts} Z"
            self.out.append(f'<path d="{d}" fill="{fill}" fill-opacity="0.15" stroke="none"/>')
        else:
            d = "M" + pts[1:]
            self.out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def raw(self, s):
        self.out.append(s)


def svg(w, h, panels, extra=""):
    body = "".join("".join(p.out) for p in panels)
    defs = ('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            '<path d="M0,1 L9,5 L0,9" fill="none" stroke="#000" stroke-width="1.4"/></marker></defs>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{defs}{body}{extra}</svg>'


def crossings(f, g, a, b, n=4000):
    """x-values in [a,b] where f(x)-g(x) changes sign: for marking intersections exactly."""
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    out = []
    for x1, x2 in zip(xs, xs[1:]):
        if (f(x1) - g(x1)) * (f(x2) - g(x2)) <= 0:
            out.append((x1 + x2) / 2)
    return out


# ---------- figure generators: one def f_<name>() per {{FIG:<name>}} ----------

def f_example_eps_band():
    """Example: an epsilon-band around L and a delta-window around c for a concave curve.
    Delete or replace; kept here to show the API."""
    f = lambda x: 1.2 + 2.2 * math.sqrt(x)
    c = 2.0; Lv = f(c); eps = 0.9
    d = 0.92 * min(c - ((Lv - eps - 1.2) / 2.2) ** 2, ((Lv + eps - 1.2) / 2.2) ** 2 - c)
    P = Panel(420, 200, (0, 4.6), (0, 6.6), pad=(46, 20, 26, 12))
    P.rect(0, Lv - eps, 4.6, Lv + eps, op=0.13)
    P.rect(c - d, 0, c + d, 6.6, op=0.13)
    for y in (Lv - eps, Lv + eps):
        P.line(0, y, 4.6, y, color=ACC, dash="3 3", width=0.8)
    for x in (c - d, c + d):
        P.line(x, 0, x, 6.6, color=ACC, dash="3 3", width=0.8)
    P.axes(xticks=[(c - d, "c − δ"), (c, "c"), (c + d, "c + δ")],
           yticks=[(Lv - eps, "L − ε"), (Lv, "L"), (Lv + eps, "L + ε")])
    P.curve(f, 0, 4.6)
    P.curve(f, c - d, c + d, n=200, width=2.6, color=ACC)
    P.line(0, Lv, c, Lv, color="#888", dash="2 2"); P.line(c, 0, c, Lv, color="#888", dash="2 2")
    P.dot(c, Lv, open_=True)
    P.text(4.5, f(4.5), "y = f(x)", anchor="end", dy=-10, size=12)
    return svg(420, 200, [P])


# ---------- driver ----------
GEN = {k[2:].replace("_", "-"): v for k, v in globals().items() if k.startswith("f_") and callable(v)}

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    html = open(src).read()
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)   # drop the template's instructional comments
    html = re.sub(r"\{\{FIG:([a-z0-9-]+)\}\}", lambda m: GEN[m.group(1)](), html)
    left = re.findall(r"\{\{FIG:[^}]*\}\}", html)
    assert not left, f"no generator for {left}"
    # keep trailing punctuation on the same line as short inline maths
    html = re.sub(r"(?<![$\\])\$(?!\$)([^$]{1,30}?)\$(?!\$)([.,;:!?)])", r'<span class="nw">$\1$\2</span>', html)
    open(dst, "w").write(html)
    print("ok", len(GEN), "figure generators")

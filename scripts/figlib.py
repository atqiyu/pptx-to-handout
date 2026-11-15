# -*- coding: utf-8 -*-
"""SVG figure toolkit: clean vector circuit diagrams and data charts."""

INK = "#1d2739"
ACC = "#1d4e89"
WARN = "#b45309"
MUTED = "#7c8899"
GREEN = "#1f6b52"
GRID = "#c9d2de"

FONT_CN = "'Microsoft YaHei','Noto Sans SC',sans-serif"
FONT_MATH = "'Times New Roman',serif"


def _s(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class C:
    """Circuit canvas."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []
        self.defs = []

    def svg(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" class="fig-svg" role="img">')
        body = "".join(self.parts)
        return head + body + "</svg>"

    def wire(self, *pts, color=INK, w=1.7, dash=None):
        d = " ".join(f"{_s(x)},{_s(y)}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def dot(self, x, y, color=INK, r=3.0):
        self.parts.append(f'<circle cx="{_s(x)}" cy="{_s(y)}" r="{r}" fill="{color}"/>')

    def rect(self, x, y, w, h, color=INK, fill="#fff", sw=1.7, rx=0):
        self.parts.append(
            f'<rect x="{_s(x)}" y="{_s(y)}" width="{_s(w)}" height="{_s(h)}" rx="{rx}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=13, color=INK, anchor="middle", italic=False,
             family=None, weight="400", baseline=None):
        fam = family or (FONT_MATH if italic else FONT_CN)
        st = ' font-style="italic"' if italic else ""
        bl = f' dominant-baseline="{baseline}"' if baseline else ""
        self.parts.append(
            f'<text x="{_s(x)}" y="{_s(y)}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}{bl}>{s}</text>')

    def var(self, x, y, s, size=14, color=INK, anchor="middle"):
        self.text(x, y, s, size=size, color=color, anchor=anchor, italic=True)

    def sub(self, x, y, s, size=10, color=None, anchor="start"):
        self.text(x, y, s, size=size, color=color or INK, anchor=anchor, family=FONT_MATH)

    # --- components -------------------------------------------------
    def resistor(self, x1, x2, y, label="", lpos="below", h=20, color=INK):
        self.rect(x1, y - h / 2, x2 - x1, h, color=color)
        if label:
            ly = y + h / 2 + 15 if lpos == "below" else y - h / 2 - 7
            self.var((x1 + x2) / 2, ly, label, color=color)

    def rheostat(self, x1, x2, y, label="", arrow_from="left", h=20, color=INK):
        self.rect(x1, y - h / 2, x2 - x1, h, color=color)
        ax = x1 + (x2 - x1) * 0.18
        self.wire((ax, y - 12), (ax, y - 30), (x2 - 6, y - 30), (x2 - 6, y - h / 2 - 1),
                  color=color, w=1.5)
        # arrow head
        self.parts.append(
            f'<path d="M {_s(x2-6)} {_s(y-h/2-1)} l -4 -6 l 8 0 z" fill="{color}"/>')
        if label:
            self.var((x1 + x2) / 2, y + h / 2 + 16, label, color=color)

    def meter(self, cx, cy, label, r=17, color=INK, sub=""):
        self.parts.append(f'<circle cx="{_s(cx)}" cy="{_s(cy)}" r="{r}" fill="#fff" stroke="{color}" stroke-width="1.7"/>')
        self.var(cx - (2 if sub else 0), cy + 5, label, size=14, color=color)
        if sub:
            self.text(cx + 8, cy + 9, sub, size=9, color=color, anchor="start", family=FONT_MATH)

    def battery(self, x, y, horizontal=True, color=INK, label="", lab_side="left"):
        """Battery centred at (x,y); long plate = +."""
        if horizontal:
            self.wire((x - 30, y), (x - 6, y), color=color)
            self.wire((x + 6, y), (x + 30, y), color=color)
            self.wire((x - 6, y - 13), (x - 6, y + 13), color=color, w=2.4)
            self.wire((x + 6, y - 7), (x + 6, y + 7), color=color, w=2.4)
        else:
            self.wire((x, y - 30), (x, y - 6), color=color)
            self.wire((x, y + 6), (x, y + 30), color=color)
            self.wire((x - 13, y - 6), (x + 13, y - 6), color=color, w=2.4)
            self.wire((x - 7, y + 6), (x + 7, y + 6), color=color, w=2.4)
        if label:
            if lab_side == "left":
                self.var(x - 8, y - 18, label, color=color, anchor="end")
            else:
                self.var(x + 8, y - 18, label, color=color, anchor="start")

    def switch(self, x1, x2, y, label="", closed=False, color=INK, lab_offset=17):
        """Two terminals at (x1,y),(x2,y)."""
        self.parts.append(f'<circle cx="{_s(x1)}" cy="{_s(y)}" r="2.8" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
        self.parts.append(f'<circle cx="{_s(x2)}" cy="{_s(y)}" r="2.8" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
        if closed:
            self.wire((x1, y), (x2, y), color=color)
        else:
            self.wire((x1 + 1, y - 2), (x2 - 3, y - 15), color=color)
        self.wire((x1 - 12, y), (x1, y), color=color)
        self.wire((x2, y), (x2 + 12, y), color=color)
        if label:
            self.text(x2 - (x2 - x1) * 0.15, y + lab_offset, label, size=12.5, color=color,
                      family=FONT_CN)

    def arrow(self, x1, y1, x2, y2, color=ACC, w=1.6, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{_s(x1)}" y1="{_s(y1)}" x2="{_s(x2)}" y2="{_s(y2)}" stroke="{color}" '
            f'stroke-width="{w}"{da} marker-end="url(#ar)"/>')
        if '<defs>' not in "".join(self.defs):
            self.defs.append(
                '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
                'markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
                f'fill="{color}"/></marker></defs>')

    def tag(self, x, y, s, color=ACC, size=11.5, anchor="middle"):
        self.text(x, y, s, size=size, color=color, anchor=anchor, weight="500")


class Chart:
    """Data chart with axes, optional grid, lines, points and annotations."""

    def __init__(self, w, h, x0, x1, y0, y1, pad=(52, 30, 46, 46), xlabel="", ylabel=""):
        self.w, self.h = w, h
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.pl, self.pt, self.pb, self.pr = pad
        self.parts = []
        self.xlabel, self.ylabel = xlabel, ylabel

    def X(self, x):
        return self.pl + (x - self.x0) / (self.x1 - self.x0) * (self.w - self.pl - self.pr)

    def Y(self, y):
        return self.h - self.pb - (y - self.y0) / (self.y1 - self.y0) * (self.h - self.pt - self.pb)

    def axes(self, xticks, yticks, grid=True, axis_y=0.0, axis_x=None):
        ax = self.Y(axis_y)
        axx = self.X(self.x0 if axis_x is None else axis_x)
        xr = self.X(self.x1)
        xl = self.X(self.x0)
        yt = self.Y(self.y1)
        # x axis
        self.parts.append(f'<line x1="{_s(xl)}" y1="{_s(ax)}" x2="{_s(xr+14)}" y2="{_s(ax)}" stroke="{INK}" stroke-width="1.5"/>')
        self.parts.append(f'<path d="M {_s(xr+14)} {_s(ax)} l -8 -4.5 l 0 9 z" fill="{INK}"/>')
        # y axis
        self.parts.append(f'<line x1="{_s(axx)}" y1="{_s(ax)}" x2="{_s(axx)}" y2="{_s(yt-14)}" stroke="{INK}" stroke-width="1.5"/>')
        self.parts.append(f'<path d="M {_s(axx)} {_s(yt-14)} l -4.5 8 l 9 0 z" fill="{INK}"/>')
        for t in yticks:
            lab = t if isinstance(t, str) else (_s(t) if abs(t) >= 1 else f"{t:g}")
            y = self.Y(float(t))
            if grid:
                self.parts.append(f'<line x1="{_s(xl)}" y1="{_s(y)}" x2="{_s(xr)}" y2="{_s(y)}" stroke="{GRID}" stroke-width="1" stroke-dasharray="4 4"/>')
            self.parts.append(f'<text x="{_s(axx-7)}" y="{_s(y+4)}" font-family="{FONT_MATH}" font-size="14" fill="{INK}" text-anchor="end">{lab}</text>')
        for t in xticks:
            lab = t if isinstance(t, str) else (_s(t) if abs(t) >= 1 else f"{t:g}")
            x = self.X(float(t))
            if grid and abs(float(t)) > 1e-9 and abs(x - axx) > 2:
                self.parts.append(f'<line x1="{_s(x)}" y1="{_s(ax)}" x2="{_s(x)}" y2="{_s(yt)}" stroke="{GRID}" stroke-width="1" stroke-dasharray="4 4"/>')
            self.parts.append(f'<text x="{_s(x)}" y="{_s(ax+17)}" font-family="{FONT_MATH}" font-size="14" fill="{INK}" text-anchor="middle">{lab}</text>')
        if self.xlabel:
            self.parts.append(f'<text x="{_s(xr)}" y="{_s(ax+34)}" font-family="{FONT_MATH}" font-size="16.5" font-style="italic" fill="{INK}" text-anchor="end">{self.xlabel}</text>')
        if self.ylabel:
            if axx - xl < 12:
                self.parts.append(f'<text x="{_s(axx+7)}" y="{_s(yt-24)}" font-family="{FONT_MATH}" font-size="16.5" font-style="italic" fill="{INK}" text-anchor="start">{self.ylabel}</text>')
            else:
                self.parts.append(f'<text x="{_s(axx-5)}" y="{_s(yt-24)}" font-family="{FONT_MATH}" font-size="16.5" font-style="italic" fill="{INK}" text-anchor="end">{self.ylabel}</text>')

    def line(self, pts, color=ACC, w=2.0, dash=None):
        d = " ".join(f"{_s(self.X(x))},{_s(self.Y(y))}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{da}/>')

    def point(self, x, y, color=INK, r=3.4):
        self.parts.append(f'<circle cx="{_s(self.X(x))}" cy="{_s(self.Y(y))}" r="{r}" fill="{color}"/>')

    def note(self, x, y, s, color=WARN, size=12, anchor="start", italic=False):
        fam = FONT_MATH if italic else FONT_CN
        st = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{_s(self.X(x))}" y="{_s(self.Y(y))}" font-family="{fam}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{st}>{s}</text>')

    def slope_tri(self, x1, y1, x2, color=MUTED, label=""):
        """Horizontal + vertical legs under the line, both legs dashed."""
        self.parts.append(f'<path d="M {_s(self.X(x1))} {_s(self.Y(y1))} L {_s(self.X(x2))} {_s(self.Y(y1))}" fill="none" stroke="{color}" stroke-width="1.1" stroke-dasharray="3 3"/>')
        if label:
            self.parts.append(f'<text x="{_s((self.X(x1)+self.X(x2))/2)}" y="{_s(self.Y(y1)+15)}" font-family="{FONT_MATH}" font-size="11.5" font-style="italic" fill="{color}" text-anchor="middle">{label}</text>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" class="fig-svg" role="img">' + "".join(self.parts) + "</svg>")

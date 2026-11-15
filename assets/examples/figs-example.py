# -*- coding: utf-8 -*-
"""Example figure module. Copy next to your parts/, then extend.

Contract expected by build.py:
    FIGS   dict {name: zero-arg callable -> C | Chart}
    render(name) -> SVG string

figlib.py lives in the skill's scripts/ directory and is added to sys.path by
build.py, so `from figlib import ...` works from any project.
"""
from figlib import C, Chart, INK, ACC, WARN, MUTED


def fig_ui_demo():
    """U-I line: intercept E, slope -r, with a slope triangle."""
    ch = Chart(400, 285, 0, 1.65, 0, 3.35, pad=(56, 38, 50, 52), xlabel="I / A", ylabel="U / V")
    ch.axes([0, 0.4, 0.8, 1.2, 1.6], [0, 1.0, 2.0, 3.0], grid=False, axis_y=0)
    ch.line([(0, 3.0), (1.5, 0)], color=ACC, w=2.2)
    ch.point(0, 3.0, color=WARN, r=3.8)
    ch.note(0.13, 3.10, "b = E", WARN, 12)
    ch.point(0.5, 2.0, color=INK, r=3.2)
    ch.point(1.0, 1.0, color=INK, r=3.2)
    ch.slope_tri(0.5, 2.0, 1.0, label="ΔI")
    ch.note(1.05, 1.42, "ΔU", MUTED, 11)
    return ch


def fig_circuit_demo():
    """Two meters, a rheostat, a battery and a switch."""
    c = C(380, 250)
    xL, xR, yT, yM, yB = 36, 344, 42, 104, 202
    c.wire((xL, yT), (xL, yB))
    c.wire((xR, yT), (xR, yB))
    c.wire((xL, yT), (58, yT))
    c.rheostat(58, 148, yT, "R")
    c.wire((148, yT), (160, yT))
    c.meter(178, yT, "A")
    c.wire((195, yT), (xR, yT))
    c.wire((xL, yM), (160, yM))
    c.meter(178, yM, "V")
    c.wire((195, yM), (xR, yM))
    c.dot(xL, yM); c.dot(xR, yM)
    c.wire((xL, yB), (48, yB))
    c.battery(78, yB, label="E")
    c.wire((108, yB), (170, yB))
    c.switch(180, 206, yB, "S")
    c.wire((206, yB), (xR, yB))
    return c


FIGS = {
    "ui_demo": fig_ui_demo,
    "circuit_demo": fig_circuit_demo,
}


def render(name):
    obj = FIGS[name]()
    svg = obj.svg()
    if isinstance(obj, C) and obj.defs:
        idx = svg.index(">") + 1
        svg = svg[:idx] + "".join(obj.defs) + svg[idx:]
    return svg
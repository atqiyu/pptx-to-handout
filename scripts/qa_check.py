#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quality gate for a built handout: overflow, page geometry, fonts, page PNGs.

Checks
  1. Content overflow  - runs the debug build in Chrome and greps the badges.
  2. Page geometry     - every PDF page must be exactly A4 (except intentional
                         inserts such as a cover or a landscape fold-out).
  3. Font embedding    - flags Type3 output, which means Chrome vectorised a
                         CFF/OTF CJK font: text stops being searchable and
                         the file balloons. Fix the CSS font stack instead.
  4. Renders           - page PNGs at the requested DPI for visual review.

Usage:
    python qa_check.py handout_dir --pdf out/handout.pdf [--dpi 150] [--out qa]
"""
import os
import re
import sys
import glob
import shutil
import argparse
import subprocess

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build.py")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "chromium", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    return None


def check_overflow(handout_dir):
    chrome = find_chrome()
    if not chrome:
        return "SKIP (no browser)"
    subprocess.run([sys.executable, BUILD, "--dir", handout_dir, "--debug", "--no-print"],
                   check=True, cwd=os.path.dirname(os.path.abspath(handout_dir)) or ".")
    url = "file:///" + os.path.join(os.path.abspath(handout_dir), "handout.html").replace("\\", "/")
    out = subprocess.run([chrome, "--headless=new", "--disable-gpu",
                          "--allow-file-access-from-files", "--virtual-time-budget=8000",
                          "--dump-dom", url],
                         capture_output=True, text=True, encoding="utf-8", errors="ignore")
    hits = re.findall(r"P(\d+) \+(\d+)px", out.stdout or "")
    return ", ".join(f"page {p} +{n}px" for p, n in hits) if hits else "OK (none)"


def check_geometry(pdf):
    doc = pymupdf.open(pdf)
    bad = []
    for i, page in enumerate(doc, 1):
        w, h = page.rect.width / 72 * 25.4, page.rect.height / 72 * 25.4
        if abs(w - 210) > 1 or abs(h - 297) > 1:
            bad.append(f"p{i}: {w:.0f}x{h:.0f}mm")
    return doc.page_count, ("OK (all A4)" if not bad else "; ".join(bad))


def check_fonts(pdf):
    doc = pymupdf.open(pdf)
    type3, names = set(), set()
    for page in doc:
        for f in page.get_fonts():
            name = f[3] or ""
            if "Type3" in name:
                type3.add(page.number + 1)
            elif name:
                names.add(name.split("+")[-1])
    if type3:
        return False, f"Type3 glyphs on pages {sorted(type3)} -> switch CJK font to a TrueType family"
    cjk = [n for n in names if any(k in n for k in ("YaHei", "SimSun", "SimHei", "Noto", "Song", "Hei"))]
    return True, "OK (" + ", ".join(sorted(cjk)[:4]) + ")"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--pdf", default="")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--out", default="qa")
    a = ap.parse_args()

    pdf = a.pdf or glob.glob(os.path.join(a.dir, "*.pdf"))[0]

    print("[1/4] overflow ...")
    print("      ", check_overflow(a.dir))
    print("[2/4] page geometry ...")
    n, geo = check_geometry(pdf)
    print(f"       {n} pages; {geo}")
    print("[3/4] fonts ...")
    ok, msg = check_fonts(pdf)
    print("      ", ("PASS " if ok else "WARN ") + msg)
    print("[4/4] renders ...")
    os.makedirs(a.out, exist_ok=True)
    doc = pymupdf.open(pdf)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=a.dpi).save(os.path.join(a.out, f"page{i:02d}.png"))
    print(f"       {n} PNGs -> {a.out}")


if __name__ == "__main__":
    main()
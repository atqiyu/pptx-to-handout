#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assemble an A4 handout from HTML parts, then print it to PDF with Chrome.

Project layout expected:

    <project>/
      handout/
        parts/p01.html, p02.html ...     one <section class="page"> per file
        theme.css                        optional overrides / page-specific CSS
        figs.py                          optional: FIG = {name: callable}
        assets/*.png                     raster assets referenced from HTML
      out/handout.pdf                    produced here

Page parts use `{{FIG:name}}` where a generated SVG should be injected, and
`$...$` / `$$...$$` for math (pre-rendered by KaTeX before printing).

Usage:
    python build.py --dir handout --out out/handout.pdf [--debug] [--no-print]
"""
import os
import re
import sys
import glob
import shutil
import argparse
import importlib.util
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)                      # skill root
BASE_CSS = os.path.join(SKILL, "assets", "base.css")
KATEX_SRC = os.path.join(SKILL, "assets", "katex")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

DEBUG_JS = """
<script>
window.addEventListener('load', () => {
  document.querySelectorAll('.page').forEach((pg, i) => {
    const c = pg.querySelector('.content');
    if (!c) return;
    const foot = pg.querySelector('.runfoot');
    const kids = [...c.children];
    if (!kids.length) return;
    const bottom = Math.max(...kids.map(k => k.getBoundingClientRect().bottom));
    const limit = foot ? foot.getBoundingClientRect().top : pg.getBoundingClientRect().bottom;
    if (bottom > limit + 1) {
      const d = document.createElement('div');
      d.style.cssText = 'position:absolute;right:2mm;bottom:1mm;background:#c00;color:#fff;font:8pt monospace;padding:1mm 2mm;z-index:99';
      d.textContent = 'P' + (i + 1) + ' +' + Math.round(bottom - limit) + 'px';
      pg.appendChild(d);
    }
  });
});
</script>"""

SHELL = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="vendor/katex/katex.min.css">
<style>
{base_css}
{theme_css}
</style></head>
<body>
{pages}
{debug}
</body></html>"""


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "chromium", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("Chrome/Edge not found; install one or print the HTML manually.")


def load_figs(figs_path):
    if not figs_path or not os.path.exists(figs_path):
        return None
    spec = importlib.util.spec_from_file_location("project_figs", figs_path)
    mod = importlib.util.module_from_spec(spec)
    # figlib.py ships with the skill; the project's figs.py does `from figlib import ...`
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(figs_path))
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="handout")
    ap.add_argument("--out", default="out/handout.pdf")
    ap.add_argument("--title", default="讲义")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--no-print", action="store_true")
    a = ap.parse_args()

    root = os.path.abspath(a.dir)
    parts = sorted(glob.glob(os.path.join(root, "parts", "p*.html")))
    if not parts:
        sys.exit(f"no parts found in {root}/parts")

    # KaTeX assets are copied in so relative URLs resolve for file:// pages.
    vk = os.path.join(root, "vendor", "katex")
    if not os.path.exists(vk):
        shutil.copytree(KATEX_SRC, vk)

    figs = load_figs(os.path.join(root, "figs.py"))

    def repl(m):
        name = m.group(1)
        if figs and hasattr(figs, "render"):
            if hasattr(figs, "FIGS") and name not in figs.FIGS:
                print(f"[warn] unknown figure: {name}")
                return f"<!-- missing figure: {name} -->"
            return figs.render(name)
        f = os.path.join(root, "figs", name + ".svg")
        if os.path.exists(f):
            return open(f, encoding="utf-8").read()
        return f"<!-- missing figure: {name} -->"

    pages = "\n".join(open(p, encoding="utf-8").read() for p in parts)
    pages = re.sub(r"\{\{FIG:(.+?)\}\}", repl, pages)

    base_css = open(BASE_CSS, encoding="utf-8").read()
    theme = os.path.join(root, "theme.css")
    theme_css = open(theme, encoding="utf-8").read() if os.path.exists(theme) else ""

    html = SHELL.format(title=a.title, base_css=base_css, theme_css=theme_css,
                        pages=pages, debug=DEBUG_JS if a.debug else "")
    src_path = os.path.join(root, "handout.src.html")
    open(src_path, "w", encoding="utf-8").write(html)

    # Math pre-render (server side: no race with the print step).
    subprocess.run(["node", os.path.join(HERE, "math.js"),
                    os.path.join(vk, "katex.min.js"),
                    src_path, os.path.join(root, "handout.html")],
                   check=True, cwd=root)

    if a.no_print:
        print("built HTML only:", os.path.join(root, "handout.html"))
        return

    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    chrome = find_chrome()
    url = "file:///" + os.path.join(root, "handout.html").replace("\\", "/")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--allow-file-access-from-files", "--virtual-time-budget=10000",
           f"--print-to-pdf={out}", url]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("PDF:", out)


if __name__ == "__main__":
    main()
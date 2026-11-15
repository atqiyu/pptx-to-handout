#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render a PPTX (or PDF) to page PNGs so the deck can actually be READ.

Chinese courseware usually keeps formulas as OLE equation objects and figures
as bitmaps, so text extraction alone loses most of the content. LibreOffice +
PyMuPDF gives a faithful picture of every slide.

Usage:
    python render_pptx.py deck.pptx out_dir [--dpi 150] [--pages 1-5,9]
"""
import os
import sys
import glob
import shutil
import argparse
import subprocess

import pymupdf


SOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
]


def find_soffice():
    for p in SOFFICE_CANDIDATES:
        if os.path.exists(p):
            return p
    p = shutil.which("soffice") or shutil.which("libreoffice")
    if p:
        return p
    sys.exit("LibreOffice not found. Install it or convert the deck to PDF manually.")


def parse_pages(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for chunk in spec.split(","):
        if "-" in chunk:
            a, b = chunk.split("-")
            out += list(range(int(a) - 1, int(b)))
        else:
            out.append(int(chunk) - 1)
    return [i for i in out if 0 <= i < n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("outdir")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--pages", default="")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    src = os.path.abspath(a.src)

    if src.lower().endswith(".pptx") or src.lower().endswith(".ppt"):
        soffice = find_soffice()
        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", a.outdir, src], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.join(a.outdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
        if not os.path.exists(pdf):
            cand = glob.glob(os.path.join(a.outdir, "*.pdf"))
            if not cand:
                sys.exit("LibreOffice produced no PDF (is a lock file open? try closing Impress).")
            pdf = cand[0]
    else:
        pdf = src

    doc = pymupdf.open(pdf)
    w_mm = doc[0].rect.width / 72 * 25.4
    h_mm = doc[0].rect.height / 72 * 25.4
    print(f"PDF: {pdf}\npages: {doc.page_count}  size: {w_mm:.1f} x {h_mm:.1f} mm")

    for i in parse_pages(a.pages, doc.page_count):
        out = os.path.join(a.outdir, f"slide{i+1:02d}.png")
        doc[i].get_pixmap(dpi=a.dpi).save(out)
    print(f"rendered to {a.outdir}")


if __name__ == "__main__":
    main()
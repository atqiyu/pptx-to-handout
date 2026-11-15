#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dump a PPTX deck's structure: slide size, shape tree, text, tables, pictures.

Most Chinese teaching decks store formulas as OLE objects and figures as
pictures, so this dump alone is NOT enough to understand a deck. Render the
deck to images too (see render_pptx.py) and read them.

Usage:
    python extract_pptx.py deck.pptx out_dir
"""
import os
import sys
import argparse

from pptx import Presentation


def walk(shapes, out, prefix, img_dir):
    for j, sh in enumerate(shapes):
        pos = (f"pos=({sh.left/914400:.2f},{sh.top/914400:.2f}) "
               f"size=({sh.width/914400:.2f}x{sh.height/914400:.2f})")
        out.append(f"{prefix}[{j}] type={sh.shape_type} name={sh.name!r} {pos}")
        if sh.has_text_frame:
            txt = []
            for p in sh.text_frame.paragraphs:
                s = "".join(r.text for r in p.runs)
                if s.strip():
                    txt.append("  " * p.level + s)
            if txt:
                out.append(prefix + "  TEXT:")
                out += [prefix + "    " + t for t in txt]
        if getattr(sh, "has_table", False) and sh.has_table:
            out.append(prefix + "  TABLE:")
            for row in sh.table.rows:
                out.append(prefix + "    | " +
                           " | ".join(c.text.replace("\n", " ") for c in row.cells) + " |")
        if sh.shape_type == 13:  # PICTURE
            try:
                img = sh.image
                fn = os.path.join(img_dir, f"{prefix.strip(' []').replace(' ', '_')}{j}.{img.ext}")
                with open(fn, "wb") as f:
                    f.write(img.blob)
                out.append(prefix + f"  IMAGE {fn} ({img.size[0]}x{img.size[1]})")
            except Exception as e:  # noqa: BLE001
                out.append(prefix + f"  IMAGE-ERR {e}")
        if sh.shape_type == 6:  # GROUP
            walk(sh.shapes, out, prefix + "  ", img_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("outdir")
    a = ap.parse_args()

    out_dir = a.outdir
    img_dir = os.path.join(out_dir, "imgs")
    os.makedirs(img_dir, exist_ok=True)

    prs = Presentation(a.pptx)
    lines = [
        f"SLIDE_SIZE_EMU {prs.slide_width} {prs.slide_height}",
        f"SLIDE_SIZE_IN {prs.slide_width/914400:.3f}x{prs.slide_height/914400:.3f}",
        f"NUM_SLIDES {len(prs.slides)}",
    ]
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"\n{'='*64}\n### SLIDE {i}\n{'='*64}")
        walk(slide.shapes, lines, "", img_dir)

    text = "\n".join(lines)
    with open(os.path.join(out_dir, "structure.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n[written] {os.path.join(out_dir, 'structure.txt')}")


if __name__ == "__main__":
    main()
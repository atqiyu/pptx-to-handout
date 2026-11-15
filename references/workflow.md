# Workflow runbook

Concrete steps, artifacts and gates for turning a deck into a handout. The
numbers come from one real run: a 21-slide Chinese physics courseware deck
(measure the EMF and internal resistance of a cell) that became a 16-page A4
handout in roughly one working session.

---

## 0. Recon — see the deck as it actually is

```bash
python scripts/extract_pptx.py "deck.pptx" work/
python scripts/render_pptx.py  "deck.pptx" work/render --dpi 150
```

Why both:

- `structure.txt` gives exact positions, text, tables, group nesting and image
  files. It is the only way to know a figure's designed size (inches) so you
  can judge whether the bitmap is high-res enough for print.
- The rendered PNGs are the only way to see formula objects (OLE), arrow
  annotations and the real visual hierarchy. On the deck that motivated this
  skill, 60 %+ of the content existed only as images: 21 slides produced only
  ~40 lines of extractable text.

**Gate:** open every `slideNN.png`. Keep a running note per slide:
`topic | figures used | answers shown | defects`. If a slide is unreadable at
150 dpi, crop the region at 300 dpi (`pymupdf` clip) before judging it.

Useful crop snippet:

```python
import pymupdf
doc = pymupdf.open("work/render/deck.pdf")
doc[14].get_pixmap(dpi=300, clip=pymupdf.Rect(x0, y0, x1, y1)).save("crop.png")
```

---

## 1. Audit — write the defect list

Do not start designing until the list exists. Two tables.

**Content inventory**

| # | Slide | Claim it makes | Figure(s) | Keep / rewrite / drop |
|---|-------|----------------|-----------|------------------------|
| 1 | cover | title + a joke pool photo | photo | drop photo |
| 2 | 原理 | E=U+Ir, two methods | circuits, graph | rewrite |
| … | | | | |

**Defects**

| Type | Example found | Action |
|------|---------------|--------|
| typo | “必需是不是从零开始的” | rewrite the sentence |
| wrong label | two different circuits both called “图1” | rename 甲/乙 and define once |
| physics error | slope labelled `k = (9.6-4.2)/1.8 = 3Ω` while the axis was already ×3 | re-derive, restate |
| answer-only | 6 exam questions with red numbers, no reasoning | write full solutions |
| unreadable | 96 dpi scans of graphs | redraw as SVG |
| duplicate | same电路图 on 4 slides | show once, reference |

**Gate:** every answer in the deck has been **re-derived by hand**. Treat the
source as untrusted: in the run above, one worked example's formula printed a
raw LaTeX error, one answer conflated the shunt resistor with the modified
meter's resistance, and one “note” was grammatical noise.

---

## 2. Architect — the A4 page map

Decide the page list before writing any HTML.

```
01 cover
02 导读     四问 + 目录 + 符号表
03 原理     方程 → 计算法 → 图像法
04 电路     甲/乙 + 步骤 + 注意事项
05 误差·甲  换分调推导 + 图像
06 误差·乙  推导 + 对照表 + 判据
07 改进     R0 / R_A / R_V 三种补丁
08 改装     电流表 / 电压表 + 换算规则
09 三法      换分调 + 安阻法
10 三法      伏阻法 + 三法对比表
11-16 真题   每题一页：题干 + 图 + 解析 + 答案
```

Rules of thumb:

- 1 deck slide ≠ 1 page. Merge thin slides (a single formula), split fat ones
  (a slide carrying statement + figure + answer).
- Order by dependency, not by the deck's order. The original put error analysis
  before the reader knew which meter sat where.
- Put all exercises at the back, sorted by skill, not by source year.
- A 16-page target for a 21-slide deck is a good ratio; 20 pages means you are
  transcribing, 10 means you cut content the teacher needs.

**Gate:** the page map fits on one screen and each line has a verb.

---

## 3. Design — build one page first

Create the theme, then compose **one** representative page (the hardest one,
usually a derivation page). Iterate on it until the navigation, hierarchy and
figure integration feel right. Only then mass-produce.

Deliverables:

```
handout/
  theme.css          project tokens + components (copy base.css as a start)
  parts/p01.html …   one <section class="page"> per file
  figs.py            SVG figure module (see assets/examples/figs-example.py)
  assets/*.png       unavoidable rasters
```

**Gate:** page renders at the right density without any `style=` patch except
one-off widths.

---

## 4. Figures — vector first

Anything with straight lines, circles, labels or axes is cheaper to redraw than
to crop, and it prints crisply at any size:

- circuits → `figlib.C` (`wire`, `resistor`, `rheostat`, `meter`, `battery`,
  `switch`, `dot`, `tag`)
- data plots → `figlib.Chart` (`axes` with `axis_x`, `line`, `point`, `note`,
  `slope_tri`)

Keep raster only for photos and instrument dials. When a bitmap must stay,
crop it from a 300–340 dpi PDF render, not from the PPTX (PowerPoint stores
cropped pictures as sub-frames of a larger source, so `shutil`-style extraction
gives you the wrong pixels).

**Gate:** each figure legible when the page is printed at A4 — smallest label
≥ 7 pt equivalent; no annotation crossing a data line.

---

## 5. Build

```bash
python scripts/build.py --dir handout --out out/handout.pdf --title "…" --debug
```

What it does, in order:

1. sorts `parts/p*.html`, joins them;
2. replaces `{{FIG:name}}` with SVG from `figs.py` (or `figs/name.svg`);
3. inlines `assets/base.css` + `handout/theme.css`;
4. copies KaTeX next to the HTML so `file://` fonts resolve;
5. pre-renders `$…$` / `$$…$$` with KaTeX in Node (no print-vs-JS race);
6. prints with `chrome --headless=new --no-pdf-header-footer --print-to-pdf`.

**Gate:** PDF exists, `pymupdf` reports 594.96 × 841.92 pt, and the text layer
contains Chinese (open it and select a paragraph).

---

## 6. QA

```bash
python scripts/qa_check.py handout --pdf out/handout.pdf --dpi 150
```

Four checks, in this order — cheapest first:

1. **Overflow.** The `--debug` build appends a red badge whose text is
   `P<n> +<px>`; `--dump-dom` + `grep` harvests them without screenshots.
2. **Geometry.** Every page must be A4; a 595×842 pt page is the proof.
3. **Fonts.** `Type3` in the font list means Chrome vectorised a CFF/OTF CJK
   font — fix the font stack (see pitfalls) and rebuild.
4. **Eyes.** Render every page at 150 dpi and read them in order. Look for
   collisions, clipped labels, orphan punctuation, ragged column heights.

Fixing overflow: shave vertical millimetres from the *tallest* element on the
page (usually a figure row or a 3-line callout), not from the whole document.
Global padding changes move every page and cost you a second pass.

**Gate:** overflow report empty, fonts clean, and a second read-through where
you find nothing to fix.

---

## 7. Deliver

- PDF next to the source deck, named `<deck>_讲义.pdf`.
- Keep the source tree (`handout/`) — the next revision is a 5-minute edit
  instead of a rebuild.
- Tell the user what changed in *content*, not just layout: corrections,
  additions, structure. That is the part they cannot see from the PDF alone.

---

## Time profile (from the real run)

| Phase | Share | Notes |
|-------|-------|-------|
| Recon | 15 % | 21 slides read at 130–150 dpi |
| Audit | 10 % | what actually improves the teaching |
| Architect + design | 20 % | one page, three iterations |
| Figures | 20 % | ~20 SVGs, reused across pages |
| Authoring | 25 % | 16 pages, ~9000 characters |
| QA + polish | 10 % | four overflow rounds, one font swap |

The QA share stays small only because the overflow check is automated. Budget
double if you plan to eyeball 16 pages manually.
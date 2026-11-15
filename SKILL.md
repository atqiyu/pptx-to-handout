---
name: pptx-to-handout
description: Turn a PPT/PPTX lecture deck (课件) into a redesigned, print-ready A4 PDF handout (讲义/学案) built with HTML + CSS + KaTeX + vector SVG figures and printed by headless Chrome. Use whenever the user asks to 重新排版 / 优化内容 / 做成讲义·学案 / 转成 PDF a deck, or wants a printable, better-structured version of slides — even if they only say "把这个 PPT 转成 PDF" or "帮我排版这份课件".
---

# PPTX → A4 handout

## The one rule

A deck is **content to be re-authored**, not a canvas to be re-flowed. Slide
numbering, "一、原实验" headers, pasted screenshots and red answer scribbles are
artifacts of the original lecture, not requirements. Write a new document whose
spine comes from the subject, then reuse the deck's substance.

If the result looks like "the same slides, taller", stop and restructure.

## Pipeline

Seven phases. Each has a gate; do not start the next phase while the current
gate is red.

| # | Phase | Gate |
|---|-------|------|
| 0 | **Recon** — extract structure, render every slide, read them | you can describe each slide's content without looking |
| 1 | **Audit** — inventory + defect list | every typo, wrong label and unverifiable answer is written down |
| 2 | **Architect** — A4 page map | each page has one job; examples come last |
| 3 | **Design** — tokens, components, page grid | one page composed and approved before mass production |
| 4 | **Figures** — vector first, raster only when unavoidable | every figure legible at its printed size |
| 5 | **Build** — parts → HTML → KaTeX → PDF | 16±4 pages, A4, no raw LaTeX |
| 6 | **QA** — overflow, geometry, fonts, eyes | zero overflow, searchable text, clean pages |
| 7 | **Deliver** — PDF next to the source + source tree kept | file opens, 594.96×841.92 pt per page |

## Commands

```bash
SKILL=~/.agents/skills/pptx-to-handout

# 0. recon
python $SKILL/scripts/extract_pptx.py deck.pptx work/          # structure.txt + imgs/
python $SKILL/scripts/render_pptx.py  deck.pptx work/render    # slide01.png ...

# 5. build (expects handout/parts/*.html, optional handout/figs.py, handout/theme.css)
python $SKILL/scripts/build.py --dir handout --out out/handout.pdf --title "…"

# 6. QA
python $SKILL/scripts/qa_check.py handout --pdf out/handout.pdf --dpi 150
```

Copy `assets/base.css` into `handout/theme.css` (or import it) and start from
`assets/examples/part-example.html` + `assets/examples/figs-example.py`.

## Page architecture defaults

A 20-slide deck becomes **14–18 A4 pages**, not 20 slides.

1. Cover (a statement, not a title dump)
2. Reading map — the four questions the handout answers + TOC + symbol table
3.…n Concept pages, one idea each: principle → circuit → error → improvement →
   method → comparison
4.…n Worked examples (真题/例题), one per page, statement + figures + solution +
   answer box
Last: quick-reference / self-check (optional)

Rules:
- One claim per page; the page title is that claim ("被「偷走」的那部分电流"),
  not a section number ("4.实验误差分析").
- Every formula the reader needs is derived once, in place, by the same three
  moves (replace → separate → arrange into y=kx+b). Repetition is the method.
- Examples show the reasoning chain, never just the answer.
- If the deck has answers scrawled over the questions, decide once: worksheet
  (blanks, answers in a box) or annotated version — don't mix.

## Print system essentials

- A4, `@page { size: A4; margin: 0 }`, each page a fixed `210mm × 297mm`
  `.page` with `overflow: hidden` and `page-break-after: always`.
- Body 10pt / 1.85, page title 19pt, section headings 11pt with a navy rule.
  Two typefaces max: one CJK sans for text, KaTeX for math.
- One accent colour per semantics: navy = structure, amber = caution,
  green = conclusion. Never colour for decoration alone.
- Figures sit in `.figbox` (hairline border, near-white fill) with a numbered
  caption. Circuit/maths drawings are SVG; only photos and instrument dials
  stay raster.
- Keep ≥ 15 mm side margins; content lives inside, nothing kisses the trim.

## Quality bar

Before delivering, every item must be true:

- No page overflows its footer (script check, not eyeballing).
- No raw LaTeX in the PDF; no `$` characters in text.
- Chinese text is searchable (no Type3 fonts in the PDF).
- Every numerical answer is re-derived from the statement, not copied.
- Figure labels are readable at the printed size (≥ 7 pt equivalent).
- No orphan "。" or single-character lines in headings/bullets.
- Every page's bottom whitespace looks chosen, not accidental.

## Where the details live

- `references/workflow.md` — phase-by-phase runbook, file tree, audit templates.
- `references/pitfalls.md` — the traps that cost real time, with the fix for each.
- `references/design-system.md` — tokens, components, figure style, page budgets.

Read `references/pitfalls.md` before phase 4; read `design-system.md` before
phase 3.
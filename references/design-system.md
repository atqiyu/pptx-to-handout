# Design system

The visual layer that makes a re-authored handout look like a designed document
rather than a taller deck. Values are the ones that produced a clean A4 print.

## Page grid

| Item | Value |
|------|-------|
| Page | A4 210 × 297 mm, `@page { size: A4; margin: 0 }` |
| Padding | 15 mm top, 17 mm sides, 11 mm bottom |
| Live area | ~176 × 271 mm |
| Running head | 6.4 mm navy square + section title + right-aligned Latin eyebrow, hairline under |
| Footer | hairline + small caps label left, `nn / NN` right, at `bottom: 6mm` |
| Break | `.page { page-break-after: always }`, `overflow: hidden` |

Because the page box is fixed, **overflow is a silent failure** — hence the
debug badge in `build.py`.

## Colour

| Token | Hex | Use |
|-------|-----|-----|
| ink | `#111a29` | headings, emphasis |
| body | `#333e4f` | paragraphs |
| muted | `#75808f` | captions, secondary notes |
| navy | `#12325c` | structure: rules, chips, section numbers |
| blue | `#1d4e89` | figure lines, links inside text |
| amber | `#b45309` | caution, “this is the trap” |
| green | `#1f6b52` | conclusions, corrections, answers |
| line | `#dfe5ee` | hairlines, table rules |
| wash | `#f5f7fb` | card background |

Semantic only. A page should read as navy-first with one accent that carries
meaning; two accents competing on one page is the usual failure.

## Type

| Role | Size / weight | Notes |
|------|---------------|-------|
| Page title (h2) | 19 pt / 700 | the claim of the page |
| Section (h3) | 11 pt / 700 | navy, 1.4 mm left rule |
| Body | 10 pt / 400, line-height 1.85 | justified, left-align inside `.sol` |
| Lead | 10.5 pt / 400, 1.9 | 2–3 lines max |
| Caption | 7.5 pt | `图 n` in bold + description |
| Eyebrow | 7.5 pt, letter-spacing .2em | uppercase Latin or a short Chinese label |
| Math | KaTeX, 1.02× body | `\dfrac` inline costs line height — prefer `a/b` in tables |

Fonts: one CJK sans (`Microsoft YaHei` first — TrueType, so Chrome embeds it and
the text stays searchable), KaTeX for math, `Times New Roman` italic for SVG
variable labels.

## Components

| Class | Purpose | Rules |
|-------|---------|-------|
| `.formula-card` | the equation that matters | navy left rule, label in caps, one display formula |
| `.kpis` / `.kpi` | two or three key quantities | equal width, big value in navy |
| `.deriv` + `.step` | three-move derivation | numbered chips (换/分/调), one line each |
| `.callout` | caution | amber rule + “易错点” label, ≤ 3 short paragraphs |
| `.note` | conclusion / insight | green rule, one paragraph |
| `.desc` | neutral description | blue-grey rule; do not use green here |
| `.figbox` | figure holder | hairline border, `#fbfcfe` fill, numbered caption |
| `.table-wrap` + `table` | comparison | navy header row, hairline rows, no zebra |
| `.exhead` | example metadata | source tag left, teaching point right |
| `.qbox` | problem statement | wash background, blanks as `.blank` |
| `.ansbox` | answers | green tint, “ANSWER” label, one line |
| `.toc` / `.obj` / `.sumcard` | front matter | dotted leaders; numbered objectives |

Density: a concept page carries **one figure + one derivation + one callout**.
Three figures means it is two pages.

## Figures

- Stroke `1.6–1.7` units in a 380–430 unit viewBox; displayed at 80–100 mm.
- Same ink for all components; accent blue only for the current/measured line.
- Dashed = ideal/true, solid = measured. Keep that convention on every graph.
- Label sizes: variables 14–16 units, Chinese annotations 10–11.5 units. At
  85 mm display width that lands near 7–9 pt.
- Every figure gets a numbered caption that says what to *see*, not what it is:
  “图 3-1 甲接法的图线绕短路点向下转动”.

## Page rhythm

Alternate dense and airy pages: derivation page → figure-heavy page → table
page. A run of five identical two-column pages reads as a spreadsheet.

Leave the bottom 15–25 mm free on concept pages; do not stretch a figure to
fill. Whitespace at the foot is margin, whitespace mid-page is a hole — fill
holes, not margins.
# Pitfalls

Every item here cost a debugging round in a real run. Each entry says what you
see, why it happens, and the fix.

## Extraction

**1. `python-pptx` shows almost no text.**
Courseware keeps formulas as `EMBEDDED_OLE_OBJECT` and figures as pictures —
none of that is text. `structure.txt` may show ~40 lines for 21 slides.
→ Always render the deck (LibreOffice → PDF → PNG) and read the images. Use
`structure.txt` for exact sizes and image files, not for content.

**2. A picture's aspect ratio doesn't match its shape box.**
The slide crops the source image (`srcRect`). Extracting `shape.image.blob`
gives you the *uncropped* source.
→ Crop from the PDF render at 300+ dpi using the shape's position in inches
(`left/914400*72` points).

## HTML / Chrome print

**3. An SVG vanishes in the PDF but shows on screen.**
Cause in practice: the SVG sat inside an absolutely positioned wrapper that
extended past the page edge (`bottom:-6mm`). Chrome drops it at print time,
silently. A second contributor: `svg { width:100%; height:auto }` with no
intrinsic size can collapse in paged media.
→ Give every `<svg>` explicit `width="W" height="H"` attributes alongside the
viewBox, and keep positioned wrappers inside the page box (positive offsets).

**4. KaTeX renders on screen but the PDF shows `$...$`.**
`--print-to-pdf` can fire before the browser-side renderer finishes.
→ Pre-render server-side with `scripts/math.js`. In the regex, inline math must
allow newlines: `\$([^$]+?)\$`, not `[^\n$]` — otherwise any formula you wrapped
across two source lines stays raw.

**5. Two flex columns end up 2:1 instead of 1:1.**
A column containing an SVG with intrinsic width contributes that width as its
min-content size; `flex: 1 1 0` alone won't shrink it.
→ Add `.cols > * { min-width: 0 }` and a matching rule for every column class
you invent (`.c-6-6 > * { flex: 1 1 0 }`). If a class has no rule, the browser
sizes by content and your layout silently collapses.

**6. A page overflows by a few millimetres and you can't see it.**
The footer is absolute, so overflowing text simply overlaps or clips.
→ Use the `--debug` badge + `--dump-dom` check. When fixing, shave the tallest
element on that page; global padding edits reshuffle every page.

## Fonts

**7. Chinese text becomes unsearchable and the PDF triples in size.**
The CJK font in the CSS stack is OTF/CFF (e.g. `Noto Sans SC (*.otf)`); Chrome
can't subset it and emits **Type3** vector glyphs.
→ Put a TrueType CJK family first: `"Microsoft YaHei", "Noto Sans SC", ...`.
Verify with `qa_check.py` (warns on Type3) or `page.get_text("dict")`.

**8. Chinese inside `\text{}` looks like a different typeface.**
KaTeX's text font has no CJK glyphs, so the browser falls back to SimSun, which
is a Song face — visibly lighter than the surrounding Hei text.
→ Add to your CSS: `.katex .text, .katex .textrm { font-family: "Microsoft YaHei", sans-serif; }`

**9. CJK quotes break the rhythm.**
ASCII `"..."` around Chinese words renders with Latin quote marks and odd
spacing.
→ Convert to `「...」` throughout. A quick regex pass over the parts is enough:
`"([^"<>]{1,24})"` → `「\1」` when the match contains a CJK character.

## Figures

**10. A reciprocal plot's intercept cannot be read.**
For `1/I–R` and `1/U–1/R` plots the y-axis must sit at x = 0, not at the left
edge of the data range (which is negative). Otherwise “intercept b” floats in
the middle of the plot and the physics is wrong.
→ `Chart.axes(..., axis_x=0)`. Also skip grid lines that coincide with the axis.

**11. Axis labels get clipped at the canvas edge.**
A right-anchored y-label near the left edge, or a long x-label at the right.
→ For a left-edge axis, anchor the y-label *start* just right of the axis; for
a mid-plot axis, anchor it *end* just left. Put x-labels below the axis,
right-aligned to the last tick, not past the arrow.

**12. Slope annotations cross the data line.**
→ Place the slope triangle on a segment of the line, put its Δ labels outside
the triangle, and keep text at least one grid step away from points.

## Content

**13. The deck's answers are wrong.**
Courseware built by hand often has label/number slips (a slope that ignored an
axis multiplier, a shunt resistance quoted as the meter's resistance).
→ Re-derive every quantity from the statement before printing it. If the
official answer is ambiguous, state the assumption in the solution.

**14. Answers spoil the exercise.**
Deciding this halfway through produces pages that mix both styles.
→ Choose at architecture time: worksheet (blanks in the statement, answers in a
final box) or annotated (answers inline). Keep it consistent across all
examples.

**15. A “note” that only restates the obvious.**
Every callout must add a distinction, a number, or a rule of thumb. If it can
be deleted without loss, delete it — the page will breathe better.

## Tooling hygiene

**16. Python heredocs mangling `\u`, `\d`, `\;` in replacements.**
Backslashes in inline scripts raise `SyntaxWarning` / `SyntaxError` and the
replacement silently no-ops.
→ Write the edit script to a file with the Write tool, or use raw strings
(`r'\underline{\qquad}'`). After a bulk replace, `grep` the target string to
confirm it actually changed.

**17. Stale renders.**
You edit, forget to re-print, then judge an old PDF.
→ Make one command produce PDF + PNGs together, and check the file timestamp.
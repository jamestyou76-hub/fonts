# Engineering Word Report Style

Use this appearance when producing a DOCX review report.

## Page and Typography

- A4 portrait by default; use landscape only for wide matrices.
- Margins: top 19 mm, bottom 18 mm, left/right 21.5 mm.
- Use `等线` for all Chinese, English, numbers, models, tables, captions, headers, and footers.
- Body: 10 pt, `#1F2933`, 1.18 line spacing, 5 pt after.
- Title: 25 pt bold, `#084C4E`.
- H1: 16 pt bold, `#084C4E`; H2: 12.5 pt bold, `#0F6B6D`; H3: 10.8 pt bold.

## Tables and Callouts

- Use black table borders.
- Header: `#0F6B6D` fill, white bold text.
- Alternate white and `#EAF3F3` body rows.
- Center short status/value fields; left-align explanations.
- Do not use fixed row heights. Repeat headers across pages.
- P0 callout: red `#A61B1B` with `#FCECEC` fill.
- Warning callout: `#8A5A00` with `#FFF6DD` fill.
- Positive conclusion: `#176B45` with `#EAF6EF` fill.

## First Page

Include report type, title, reviewed baseline, overall conclusion, metadata table, and key-findings table. Do not create a mostly empty decorative cover.

## Figures

Crop only the relevant schematic region. Keep text readable and add: `图 N 说明（摘自原理图第 X 页）`.

## QA

Render the final DOCX to PDF/PNG and inspect every page. Check missing glyphs, clipping, table overflow, repeated headers, image resolution, page breaks, page numbers, and consistency of calculations between the summary and body.

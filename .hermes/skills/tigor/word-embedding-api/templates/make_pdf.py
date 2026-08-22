#!/usr/bin/env python3
"""markdown → PDF via WeasyPrint — known-good template for word-embedding reports."""
from markdown import markdown
from weasyprint import HTML

# ── CSS that produces stable A4 PDF with Cyrillic ──
CSS = """
@page {
    size: A4;
    margin: 18mm 15mm 20mm 15mm;
    @bottom-center {
        content: "Стр. " counter(page);
        font-size: 9pt;
        color: #888;
    }
}
@font-face { font-family: 'D'; src: local('DejaVu Sans'); }
@font-face { font-family: 'D'; src: local('DejaVu Sans-Bold'); font-weight: bold; }
@font-face { font-family: 'M'; src: local('DejaVu Sans Mono'); }

body {
    font-family: 'D', sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111;
}
h1 { font-size: 22pt; color: #b00020; border-bottom: 2px solid #b00020; padding-bottom: 6pt; margin-top: 0; }
h2 { font-size: 15pt; color: #222; border-bottom: 1px solid #ccc; padding-bottom: 4pt; margin-top: 18pt; }
h3 { font-size: 12pt; color: #444; margin-top: 14pt; margin-bottom: 6pt; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #ddd;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}
th { background: #f2f2f2; font-weight: bold; }
tr:nth-child(even) { background: #fafafa; }

code {
    font-family: 'M', monospace;
    background: #f4f4f4;
    padding: 1px 3px;
    border-radius: 2px;
    font-size: 0.9em;
    white-space: pre-wrap;
    word-break: break-word;
}
pre {
    background: #f4f4f4;
    padding: 8pt 10pt;
    border-radius: 4px;
    font-size: 9pt;
    page-break-inside: avoid;
}
pre code { background: none; padding: 0; }
blockquote {
    border-left: 4px solid #b00020;
    margin: 10pt 0;
    padding: 8pt 12pt;
    background: #f9f9f9;
    font-size: 9.5pt;
}
strong { color: #b00020; }
hr { border: none; border-top: 1px solid #ddd; margin: 14pt 0; }
"""

def md_table(rows, cols):
    h = "| " + " | ".join(cols) + " |\n"
    s = "| " + " | ".join(["---"] * len(cols)) + " |\n"
    return h + s + "".join("| " + " | ".join(r) + " |\n" for r in rows)

def render_pdf(md_text, out_path):
    html = markdown(md_text, extensions=["tables", "fenced_code"])
    doc = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<style>{CSS}</style></head><body>{html}</body></html>"""
    HTML(string=doc).write_pdf(out_path)

# ── Example usage ──
if __name__ == "__main__":
    import json
    from datetime import datetime

    with open("examples.json") as f:
        data = json.load(f)

    by_type = {}
    for i in data:
        by_type.setdefault(i["type"], []).append(i)

    type_meta = {"Аналогия": "A - B + C", "Умножение": "2×A - B", "Произведение": "A×B - C"}
    md = f"# WordCalc — Векторная арифметика слов\n\n> {len(data)} операций · {datetime.now():%d.%m.%Y}\n\n---\n\n"
    for t, desc in type_meta.items():
        items = sorted(by_type.get(t, []), key=lambda x: -x["score"])
        if not items: continue
        rows = [[f"{i:2d}", f"`{r['expr']}`", f"**{r['clean']}**", f"{r['score']:.3f}"]
                for i, r in enumerate(items, 1)]
        md += f"### {t} ({desc}) — {len(items)}\n\n"
        md += md_table(rows, ["#", "Выражение", "Результат", "Score"]) + "\n"

    render_pdf(md, "wordcalc_examples.pdf")
    print(f"✅ wordcalc_examples.pdf")

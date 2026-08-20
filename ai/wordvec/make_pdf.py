#!/usr/bin/env python3
"""markdown → PDF генератор для WordCalc (WeasyPrint)"""
import json
from markdown import markdown
from weasyprint import HTML
from datetime import datetime

DATA = "/home/hermes/projects/wordvec-api/examples.json"
MD_OUT = "/home/hermes/projects/wordvec-api/wordcalc_examples.md"
PDF_OUT = "/home/hermes/projects/wordvec-api/wordcalc_examples.pdf"

with open(DATA) as f:
    data = json.load(f)

by_type = {}
for i in data:
    by_type.setdefault(i["type"], []).append(i)

def md_table(rows, cols):
    h = "| " + " | ".join(cols) + " |\n"
    s = "| " + " | ".join(["---"]*len(cols)) + " |\n"
    return h + s + "".join(f"| " + " | ".join(r) + " |\n" for r in rows)

cats = {"Род":"👨‍👩‍👧‍👦","Антонимы":"↔️","География":"🌍","Животные":"🐾","Масштаб":"📏","Эмоции":"💭","Действия":"⚡"}
by_cat = {}
for i in data:
    by_cat.setdefault(i["cat"], []).append(i)

md = f"""# WordCalc — Векторная арифметика слов

> Word2Vec · RusCorpora · 185 000 слов · 300D · {len(data)} операций
>
> Сгенерировано {datetime.now():%d.%m.%Y %H:%M}

---

## Как это работает

Каждое слово представлено вектором из 300 чисел. Похожие слова имеют близкие векторы, поэтому над ними можно делать математику.

| Операция | Пример | Эффект |
|----------|--------|--------|
| `A - B + C` | `король - мужчина + женщина` | Аналогия: сдвигает отношение B→A на C |
| `2*A - B` | `2*внук - мужчина` | Интенсификация A минус контекст B |
| `A×B - C` | `кошка×человек - животное` | Пересечение признаков A∩B, вычитание C |
| `сумма(A,B,C)` | `сумма(кот, собака, мышь)` | Центроид категории |

---

"""

# Таблицы по типам
type_meta = {"Аналогия":("🔷","A - B + C"),"Умножение":("🟠","2×A - B"),"Произведение":("🟣","A×B - C")}
for t, (emoji, desc) in type_meta.items():
    items = sorted(by_type.get(t, []), key=lambda x: -x["score"])
    if not items: continue
    rows = []
    for i, r in enumerate(items, 1):
        rows.append([f"{i:2d}", f"`{r['expr']}`", f"**{r['clean']}**", f"{r['score']:.3f}"])
    md += f"### {emoji} {t} ({desc}) — {len(items)}\n\n"
    md += md_table(rows, ["#", "Выражение", "→ Результат", "Score"])
    md += "\n"

# Топ по категориям
md += "---\n\n## 🏆 Лучшие по категориям\n\n"
for cat, em in cats.items():
    top = sorted(by_cat.get(cat, []), key=lambda x: -x["score"])[:3]
    if not top: continue
    md += f"### {em} {cat}\n\n"
    for r in top:
        md += f"- `{r['expr']}` → **{r['clean']}** ({r['score']:.3f}) [`{r['type']}`]\n"
    md += "\n"

# API и Docker
md += """---

## 🖥️ API

```bash
# Аналогия
curl -X POST http://localhost:8000/calc \\
  -H 'Content-Type: application/json' \\
  -d '{"expression": "король - мужчина + женщина"}'

# Умножение
curl -X POST http://localhost:8000/calc \\
  -H 'Content-Type: application/json' \\
  -d '{"expression": "2*внук - мужчина"}'

# Сумма
curl -X POST http://localhost:8000/calc \\
  -H 'Content-Type: application/json' \\
  -d '{"expression": "сумма(кот, собака, мышь)"}'
```

## 🐳 Docker

```bash
podman build -t wordvec-api .
podman run -p 8000:8000 wordvec-api
```

---

*Сгенерировано WordCalc · scout.py + make_pdf.py*
"""

with open(MD_OUT, "w", encoding="utf-8") as f:
    f.write(md)
print(f"✅ {MD_OUT}")

# CSS для стабильного PDF
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
    orphans: 3;
    widows: 3;
}
h1 { font-size: 22pt; color: #b00020; border-bottom: 2px solid #b00020; padding-bottom: 6pt; margin-top: 0; }
h2 { font-size: 15pt; color: #222; border-bottom: 1px solid #ccc; padding-bottom: 4pt; margin-top: 18pt; }
h3 { font-size: 12pt; color: #444; margin-top: 14pt; margin-bottom: 6pt; }
p { margin: 6pt 0; }

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
th { background: #f2f2f2; font-weight: bold; color: #333; }
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
    overflow: hidden;
}
pre code { background: none; padding: 0; }

blockquote {
    border-left: 4px solid #b00020;
    margin: 10pt 0;
    padding: 8pt 12pt;
    background: #f9f9f9;
    color: #444;
    font-size: 9.5pt;
}
strong { color: #b00020; }
hr { border: none; border-top: 1px solid #ddd; margin: 14pt 0; }
ul { margin: 6pt 0; padding-left: 20pt; }
li { margin-bottom: 4pt; }
"""

html = markdown(md, extensions=["tables", "fenced_code"])
doc = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<style>{CSS}</style></head><body>{html}</body></html>"""

HTML(string=doc).write_pdf(PDF_OUT)
print(f"✅ {PDF_OUT}")

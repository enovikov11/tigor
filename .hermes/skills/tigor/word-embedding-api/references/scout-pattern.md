# Scout Pattern — Auto-Discovery of Interesting Word Operations

## Overview

`scout.py` loads the same gensim model as the API and programmatically tests
curated word triples through multiple operation types, collecting high-score
results for report generation.

## Operation types tested

1. **Analogy** `A - B + C` — classical vector arithmetic
2. **Intensification** `2*A - B` — doubled entity minus context
3. **Product** `A×B - C` — normalized vector product (intersection of features)

## Category patterns

```python
categories = {
    "Род": [
        ("король", "мужчина", "женщина"),
        ("брат", "мальчик", "девочка"),
        ("племянник", "мальчик", "девочка"),
        ("сын", "мужчина", "женщина"),
        ("внук", "мужчина", "женщина"),
    ],
    "Антонимы": [
        ("большой", "маленький", "огромный"),
        ("высокий", "низкий", "гигантский"),
        ("старый", "молодой", "древний"),
    ],
    "География": [
        ("москва", "россия", "париж"),
        ("берлин", "германия", "лондон"),
    ],
    "Животные": [
        ("кошка", "животное", "человек"),
        ("собака", "животное", "человек"),
    ],
    "Масштаб": [
        ("город", "село", "деревня"),
        ("океан", "море", "река"),
    ],
}
```

## Scoring function

```python
def score(expr, result_vec, source_words, topn=3):
    hits = model.most_similar([result_vec], topn=topn)
    source_set = {clean_tag(sw) for sw in source_words}
    for w, s in hits:
        if clean_tag(w) not in source_set and s > 0.4:
            return {"word": w, "score": round(float(s), 3), "clean": clean_tag(w)}
    return None
```

Key: exclude source words from results, require minimum similarity 0.4.

## Top results (RusCorpora 300D)

| Rank | Expression | Result | Score | Type |
|------|-----------|--------|-------|------|
| 1 | брат - мальчик + девочка | сестра | 0.820 | Analogy |
| 2 | племянник - мальчик + девочка | племянница | 0.794 | Analogy |
| 3 | сын - мужчина + женщина | дочь | 0.781 | Analogy |
| 4 | 2*собака - животное | пес | 0.720 | Intensification |
| 5 | 2*внук - мужчина | правнук | 0.705 | Intensification |
| 6 | 2*город - село | столица | 0.663 | Intensification |
| 7 | 2*дед - дедушка | прадед | 0.606 | Intensification |
| 8 | 2*спать - бодрствовать | заснуть | 0.667 | Intensification |

## Output format

`examples.json` — array of objects:
```json
{
  "cat": "Род",
  "expr": "брат - мальчик + девочка",
  "word": "сестра_NOUN",
  "score": 0.82,
  "clean": "сестра",
  "type": "Аналогия"
}
```

## PDF report generation

Use `make_pdf.py`:
1. Read `examples.json`
2. Generate markdown with tables grouped by operation type
3. Convert via `markdown` → HTML → `weasyprint` → PDF

```bash
pip install markdown weasyprint
python3 make_pdf.py
# → wordcalc_examples.md, wordcalc_examples.pdf
```

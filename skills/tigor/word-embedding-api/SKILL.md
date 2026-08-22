---
name: word-embedding-api
description: >
  Build a FastAPI + Docker service for word vector math — similarity, analogy,
  scalar multiplication, semantic averages, auto-discovery of interesting
  operations, and PDF report generation using gensim Word2Vec models.
---

# Word Embedding API Service

Build a FastAPI + Docker service for word vector math. Supports arithmetic
(`A - B + C`), scalar multiplication (`2*A - B`), semantic averages (`сумма()`),
analogies (`A : B :: C`), and automated discovery of high-score operations.

## Triggers

- Building a REST API around word2vec / fasttext / GloVe models
- Containerizing gensim services with FastAPI
- Word vector arithmetic, analogy detection, semantic similarity endpoints
- Auto-discovering interesting word relationships via scripted search
- Generating PDF reports from vector math results

## Architecture

Single Docker container: `python:3.11-slim` → FastAPI + gensim + runtime model download.
Primary endpoint: `POST /calc { "expression": "..." }` — calculator-style interface.

## Steps

### 1. Requirements — PIN VERSIONS

**CRITICAL:** `scipy>=1.12` removed `np.triu` which gensim 4.3.2 depends on. Always pin `scipy<1.12`.

```
fastapi==0.115.0
uvicorn==0.30.6
scipy<1.12
gensim==4.3.2
numpy==1.26.4
```

### 2. Model selection

For Russian: `word2vec-ruscorpora-300` (~185K words, 300D).
See available: `gensim.downloader.info()['models']`

Load at startup:
```python
import gensim.downloader as api
model = api.load("word2vec-ruscorpora-300")
```

### 3. POS-tag fallback (CRITICAL for RusCorpora)

RusCorpora stores words as `word_NOUN`, `word_VERB`, etc. Users input bare words:

```python
def find_word(word):
    word = word.strip().lower()
    if word in model: return word
    for tag in ["_NOUN","_VERB","_ADJ","_ADV","_ADP","_NUM","_PRON","_SCONJ"]:
        if f"{word}{tag}" in model: return f"{word}{tag}"
    return None
```

### 4. Expression parser with scalar multiplication

Supports `+`, `-`, scalar coefficients (`2*`, `/3`), and analogies (`::`):

```python
import re

def parse_expr(expr):
    """Normalize operators around tokens, then sequential parse."""
    normalized = re.sub(r'([+\-*/])', r' \1 ', expr)
    tokens = normalized.split()
    out, coeff, op = [], 1.0, "+"
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ('+', '-'):
            op = t; i += 1; continue
        if t in ('*', '/'):
            try:
                c = float(tokens[i+1])
                coeff *= c if t == '*' else 1.0/c
                i += 2; continue
            except (ValueError, IndexError): pass
        w = t.strip()
        if not w: i += 1; continue
        key = find_word(w)
        if not key: raise ValueError(f"Word not found: {w}")
        out.append((coeff if op == '+' else -coeff, key))
        coeff, op = 1.0, "+"; i += 1
    return out
```

**Analogy** (`A : B :: C`):
```python
if "::" in expr:
    left_str, right_str = expr.split("::")
    # MUST use ' - ' with spaces — ' - ' without spaces creates
    # unparsed tokens like 'Москва-Россия' that find_word can't match.
    left_str = re.sub(r'\s*:\s*', ' - ', left_str)
    # Strip BOTH colons and question marks from right side
    right_str = re.sub(r'[:?]', '', right_str).strip()
    left, right = parse_expr(left_str), parse_expr(right_str)
    # Result: (left_vec) + right[0]
```

**`сумма()` / `mean()`** — semantic average:
```python
if expr.startswith("сумма(") or expr.startswith("mean("):
    inner = expr.split("(", 1)[1].rstrip(")")
    keys = [find_word(w) for w in inner.split(",")]
    keys = [k for k in keys if k]
    v = sum((model.get_vector(k) for k in keys), zero_vec()) / len(keys)
```

### 5. Zero vector helper

```python
def zero_vec():
    return model.get_vector("человек_NOUN") * 0
```

### 6. Calculator endpoint

```python
@app.post("/calc")
def calculate(req: CalcRequest):
    words = parse_expr(req.expression)
    v = zero_vec()
    for coeff, key in words:
        v += coeff * model.get_vector(key)
    hits = model.most_similar([v], topn=10)
    return {"expression": req.expression, "result": [
        {"word": w, "score": round(float(sc), 3)} for w, sc in hits
    ]}
```

### 7. Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. Auto-discovery of interesting operations (scout)

Write `scout.py` that loads the model directly and tests curated categories:

```python
# Categories: gender, antonyms, geography, animals, scale, emotions, actions
categories = {
    "Род": [("король","мужчина","женщина"), ("брат","мальчик","девочка"), ...],
    "Антонимы": [("большой","маленький","огромный"), ...],
}

for cat, triples in categories.items():
    for a, b, c in triples:
        ka, kb, kc = find(a), find(b), find(c)
        if not all([ka, kb, kc]): continue
        # A - B + C (analogy)
        v = model[ka] - model[kb] + model[kc]
        # 2*A - B (intensification)
        v = 2*model[ka] - model[kb]
```

Filter results: exclude source words from output, require score > 0.4.
Sort by score, save to `examples.json`.

See `references/scout-pattern.md` for full script structure.

### 9. Markdown → PDF report (WeasyPrint with explicit CSS)

Generate markdown from `examples.json`, convert via `markdown` + `weasyprint`:

```bash
pip install markdown weasyprint
```

**CRITICAL for stable PDF layout:** WeasyPrint needs explicit CSS — without it tables overflow,
code blocks break, and Cyrillic renders with wrong fonts. Always embed a full CSS block with:
- `@page { size: A4; margin: 18mm 15mm 20mm 15mm; }` for page geometry
- `@font-face` pointing to DejaVu Sans/Sans Mono (installed as `fonts-dejavu-core` on Debian/Ubuntu)
- Explicit `width: 100%` and `border-collapse: collapse` on tables
- `white-space: pre-wrap` and `word-break: break-word` on `code` elements
- `page-break-inside: avoid` on tables and `pre` blocks

```python
from markdown import markdown
from weasyprint import HTML

md = generate_markdown(data)  # tables by type, top-by-category
html = markdown(md, extensions=["tables", "fenced_code"])
doc = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<style>{CSS}</style></head><body>{html}</body></html>"""
HTML(string=doc).write_pdf("wordcalc_examples.pdf")
```

Full CSS template and generation script in `references/scout-pattern.md`.

## Pitfalls

1. **scipy>=1.12 breaks gensim** — pin `scipy<1.12`. Error: `AttributeError: module 'numpy' has no attribute 'triu'`.

2. **numpy.float32 not JSON-serializable** — always `round(float(score), 3)`.

3. **Model download on first start** — gensim caches in `~/.gensim/`. First start: 60+ sec.

4. **RusCorpora POS-tags** — without `find_word()` fallback, bare words return None.

5. **Cyrillic in GET query params** — URL encoding breaks. Always POST with JSON body.

6. **`sum()` with numpy arrays** — needs generator parens: `sum((model.get_vector(k) for k in keys), zero_vec())`.

7. **Parser eats first letters** — `re.findall(r'([+\\-])\\s*(\\S+)|(\\S+)')` has bugs with hyphenated tokens. Use normalize-then-split pattern: `re.sub(r'([+\\-\\*/])', r' \\1 ', expr).split()`.

8. **Analogy `:` replacement must include spaces** — `left_str.replace(":", "-")` creates fused tokens like `Москва-Россия` that `find_word` can't parse. Use `re.sub(r'\\s*:\\s*', ' - ', left_str)` instead.

9. **Analogy right side needs `?` stripped too** — `Москва : Россия :: Париж : ?` — the trailing `?` becomes a token. Strip both: `re.sub(r'[:?]', '', right_str).strip()`.

10. **WeasyPrint without explicit CSS produces broken layout** — tables overflow page width, `code` blocks don't wrap, Cyrillic renders with fallback fonts. Must embed full CSS with `@page { size: A4; margin: ... }`, `@font-face { src: local('DejaVu Sans') }`, `code { white-space: pre-wrap; word-break: break-word }`, `table { width: 100%; border-collapse: collapse }`, and `page-break-inside: avoid` on tables/pre. Without these, the PDF looks scrambled.

## Example results (real gensim output)

```
брат - мальчик + девочка    → сестра        (0.820)
2*внук - мужчина            → правнук       (0.705)
2*собака - животное         → пес           (0.720)
2*город - село              → столица       (0.663)
2*дед - дедушка             → прадед        (0.606)
2*спать - бодрствовать      → заснуть       (0.667)
```

See `references/scout-pattern.md` for the full auto-discovery approach.

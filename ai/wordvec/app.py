from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import gensim.downloader as api

model = api.load("word2vec-ruscorpora-300")
app = FastAPI(title="WordCalc")

class CalcRequest(BaseModel):
    expression: str

def find_word(word):
    word = word.strip().lower()
    if word in model:
        return word
    for tag in ["_NOUN", "_VERB", "_ADJ", "_ADV", "_ADP", "_NUM", "_PRON", "_SCONJ"]:
        key = f"{word}{tag}"
        if key in model:
            return key
    return None

def zero_vec():
    return model.get_vector("человек_NOUN") * 0

def v(key):
    return model.get_vector(key)

def parse_expr(expr):
    # Поддерживает: +, -, * (/)
    # 2*король - мужчина + женщина
    normalized = re.sub(r'([+\-\*/])', r' \1 ', expr)
    tokens = normalized.split()
    if not tokens:
        raise ValueError("Пустое выражение")
    out = []
    i = 0
    coeff = 1.0
    op = "+"
    while i < len(tokens):
        t = tokens[i]
        if t in ('+', '-'):
            op = t
            i += 1
            continue
        if t in ('*', '/'):
            next_i = i + 1
            if next_i < len(tokens) and tokens[next_i] in ('+', '-'):
                next_i += 1
            # числовой коэффициент
            try:
                c = float(tokens[next_i])
                coeff *= c if t == '*' else 1.0 / c
                i = next_i + 1
                continue
            except ValueError:
                pass
        w = t.strip()
        if not w:
            i += 1
            continue
        key = find_word(w)
        if not key:
            raise ValueError(f"Слово не найдено: {w}")
        final_coeff = coeff if op == '+' else -coeff
        out.append((final_coeff, key))
        coeff = 1.0
        op = "+"
        i += 1
    return out

@app.get("/")
def root():
    return {
        "name": "WordCalc",
        "vocab": len(model),
        "dim": model.vector_size,
        "hint": "POST /calc { \"expression\": \"король - мужчина + женщина\" }",
        "examples": [
            "король - мужчина + женщина",
            "2*королева - король",
            "сумма(кот, собака, мышь)",
            "Москва : Россия :: Париж",
        ]
    }

@app.post("/calc")
def calculate(req: CalcRequest):
    expr = req.expression.strip()
    try:
        if "::" in expr:
            left_str, right_str = expr.split("::")
            left_str = re.sub(r'\s*:\s*', ' - ', left_str)
            right_str = re.sub(r'[:?]', '', right_str).strip()
            left = parse_expr(left_str)
            right = parse_expr(right_str)
            result_vec = zero_vec()
            for c, w in left:
                result_vec += c * v(w)
            result_vec += v(right[0][1])
            hits = model.most_similar([result_vec], topn=10)
            return {"expression": expr, "result": [{"word": w, "score": round(float(sc), 3)} for w, sc in hits]}

        if expr.startswith("сумма(") or expr.startswith("mean("):
            inner = expr.split("(", 1)[1].rstrip(")")
            keys = [find_word(w) for w in inner.split(",")]
            keys = [k for k in keys if k]
            if not keys:
                raise ValueError("Список пуст")
            result_vec = sum((v(k) for k in keys), zero_vec()) / len(keys)
            hits = model.most_similar([result_vec], topn=5)
            return {"expression": expr, "result": [{"word": w, "score": round(float(sc), 3)} for w, sc in hits]}

        pairs = parse_expr(expr)
        result_vec = zero_vec()
        for c, w in pairs:
            result_vec += c * v(w)
        hits = model.most_similar([result_vec], topn=10)
        return {"expression": expr, "result": [{"word": w, "score": round(float(sc), 3)} for w, sc in hits]}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
def info():
    sample = list(model.key_to_index.keys())[:10]
    return {
        "model": "word2vec-ruscorpora-300",
        "vocab": len(model),
        "dim": model.vector_size,
        "sample_words": sample,
    }

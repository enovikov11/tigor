#!/usr/bin/env python3
"""Сапёр интересных слово-математических операций."""
import json
import itertools
import gensim.downloader as api
import re

model = api.load("word2vec-ruscorpora-300")

def find(w):
    w = w.strip().lower()
    if w in model: return w
    for t in ["_NOUN","_VERB","_ADJ","_ADV","_ADP","_NUM","_PRON","_SCONJ","_AUX","_CCONJ","_PART"]:
        k = f"{w}{t}"
        if k in model: return k
    return None

def v(k): return model.get_vector(k)
def zero(): return v("человек_NOUN") * 0
def norm(x):
    import math
    s = math.sqrt((x*x).sum())
    return x / s if s > 0 else x

def score(expr, result_vec, source_words, topn=3):
    """Интересность: высокая сходимость с результатом + далеко от исходных слов."""
    hits = model.most_similar([result_vec], topn=topn)
    if not hits: return None
    best_word, best_score = hits[0]
    # Исключаем исходные слова из результата
    source_set = {sw.replace("_NOUN","").replace("_VERB","").replace("_ADJ","").replace("_ADV","") for sw in source_words}
    for w, s in hits:
        clean = re.sub(r'_\w+$', '', w)
        if clean not in source_set and s > 0.4:
            return {"word": w, "score": round(float(s), 3), "clean": clean}
    return None

def zero_vec():
    return v("человек_NOUN") * 0

# Категории слов
categories = {
    "Род": [
        ("король", "мужчина", "женщина"),
        ("брат", "мальчик", "девочка"),
        ("дед", "дедушка", "бабушка"),
        ("дядя", "дядька", "тётка"),
        ("зять", "муж", "жена"),
        ("племянник", "мальчик", "девочка"),
        ("кузен", "мужчина", "женщина"),
        ("сын", "мужчина", "женщина"),
        ("внук", "мужчина", "женщина"),
        ("племянница", "женщина", "мужчина"),
    ],
    "Антонимы": [
        ("большой", "маленький", "огромный"),
        ("горячий", "тёплый", "кипяток"),
        ("быстрый", "медленный", "мгновенный"),
        ("тёмный", "серый", "чёрный"),
        ("хороший", "плохой", "прекрасный"),
        ("высокий", "низкий", "гигантский"),
        ("старый", "молодой", "древний"),
        ("тяжёлый", "лёгкий", "свинцовый"),
    ],
    "География": [
        ("москва", "россия", "париж"),
        ("берлин", "германия", "лондон"),
        ("токио", "япония", "пекин"),
        ("мексика", "мексика", "оттава"),
        ("буэнос-айрес", "аргентина", "лима"),
    ],
    "Животные": [
        ("кошка", "животное", "человек"),
        ("собака", "животное", "человек"),
        ("рак", "животное", "человек"),
        ("лев", "животное", "человек"),
        ("крыса", "грызун", "человек"),
    ],
    "Масштаб": [
        ("город", "село", "деревня"),
        ("континент", "страна", "город"),
        ("дом", "комната", "шкаф"),
        ("океан", "море", "река"),
    ],
    "Эмоции": [
        ("радость", "грусть", "счастье"),
        ("любовь", "ненависть", "страсть"),
        ("восторг", "удовольствие", "экстаз"),
    ],
    "Действия": [
        ("бежать", "ходить", "лететь"),
        ("спать", "бодрствовать", "дремать"),
        ("думать", "чувствовать", "мечтать"),
    ],
}

results = []

print("🔍 Сапёр интересных операций...")
print()

for cat, triples in categories.items():
    print(f"  {cat} ({len(triples)} паттернов)...")
    for a, b, c in triples:
        ka, kb, kc = find(a), find(b), find(c)
        if not all([ka, kb, kc]):
            continue

        # A - B + C (классика)
        vec1 = v(ka) - v(kb) + v(kc)
        r1 = score(f"{a} - {b} + {c}", vec1, [ka, kb, kc])
        if r1:
            results.append({"cat": cat, "expr": f"{a} - {b} + {c}", **r1, "type": "Аналогия"})

        # 2*A - B (удвоенная сущность минус контекст)
        vec2 = 2*v(ka) - v(kb)
        r2 = score(f"2*{a} - {b}", vec2, [ka, kb])
        if r2:
            results.append({"cat": cat, "expr": f"2*{a} - {b}", **r2, "type": "Умножение"})

        # A - B + C - D (если есть четвёртое)
        # A*C - B (умноженное отношение)
        vec3 = norm(v(ka)) * norm(v(kc)) - v(kb)
        r3 = score(f"{a}×{c} - {b}", vec3, [ka, kb, kc])
        if r3:
            results.append({"cat": cat, "expr": f"{a}×{c} - {b}", **r3, "type": "Произведение"})

# Сортируем по score
results.sort(key=lambda x: x["score"], reverse=True)

# Сохраняем
with open("/home/hermes/projects/wordvec-api/examples.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Найдено {len(results)} результатов, топ-40 в examples.json")
print("\n🏆 Топ-20:")
for i, r in enumerate(results[:20]):
    print(f"  {i+1:2d}. {r['expr']:40s} → {r['clean']} ({r['score']:.3f})  [{r['type']}]")

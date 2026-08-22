import re
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

lines = []
for log in ["/opt/data/logs/agent.log", "/opt/data/logs/agent.log.1"]:
    with open(log) as f:
        lines.extend(f.readlines())

pat = re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}):\d{2}.*model=Qwen3\.6-27B-FP8.*in=(\d+)\s+out=(\d+)\s+total=(\d+)')
by_day = defaultdict(lambda: defaultdict(lambda: {"in": 0, "out": 0, "total": 0, "calls": 0}))
for line in lines:
    m = pat.search(line)
    if m:
        day, hour, inp, out, total = m.groups()
        by_day[day][hour]["in"] += int(inp)
        by_day[day][hour]["out"] += int(out)
        by_day[day][hour]["total"] += int(total)
        by_day[day][hour]["calls"] += 1

days = sorted(by_day.keys())

def fmt(n):
    if n >= 1000000: return f"{n/1e6:.1f}M"
    if n >= 1000: return f"{n//1000}K"
    return str(n)

rate_in = 0.20 / 1000000
rate_out = 0.60 / 1000000
daily = {}
for day in days:
    hs = by_day[day]
    d_in = sum(hs[h]["in"] for h in hs)
    d_out = sum(hs[h]["out"] for h in hs)
    daily[day] = {
        "in": d_in, "out": d_out, "total": d_in + d_out,
        "calls": sum(hs[h]["calls"] for h in hs),
        "cost": d_in * rate_in + d_out * rate_out
    }

g_in = sum(v["in"] for v in daily.values())
g_out = sum(v["out"] for v in daily.values())
g_total = sum(v["total"] for v in daily.values())
g_calls = sum(v["calls"] for v in daily.values())
g_cost = sum(v["cost"] for v in daily.values())
mx = max(v["total"] for v in daily.values())

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
fontB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 11)
fontT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 13)
ML, MT, RH = 30, 35, 26
BAR_X, BAR_W = 530, 230

def draw_table(d, y0, title, rows_data, totals, show_bar=True):
    d.text((ML, 8), title, fill="#58a6ff", font=fontT)
    # header
    d.rectangle([ML-5, y0-16, ML-5+740, y0+6], fill="#161b22")
    for xo, txt, clr in rows_data[0]["hdr"]:
        d.text((xo, y0-14), txt, fill=clr, font=fontB)
    # data rows
    ri = 0
    for rd in rows_data[1:]:
        y = y0 + 22 + ri * RH
        bg = "#0d1117" if ri % 2 == 0 else "#131923"
        d.rectangle([ML-5, y-15, ML-5+740, y+9], fill=bg)
        for xo, txt, clr in rd["cells"]:
            d.text((xo, y-13), txt, fill=clr, font=font)
        if show_bar and "bar_val" in rd:
            bw = int((rd["bar_val"] / mx) * BAR_W)
            d.rectangle([BAR_X+10, y-10, BAR_X+10+bw, y+4], fill="#7c3aed")
        ri += 1
    # total row
    y = y0 + 22 + ri * RH + 4
    d.rectangle([ML-5, y-15, ML-5+740, y+9], fill="#1f2a37")
    for xo, txt, clr in totals:
        d.text((xo, y-13), txt, fill=clr, font=fontB)

# TABLE 1: Tokens
nr1 = len(days) + 2
W1 = 800
H1 = MT + nr1 * RH + 40
img1 = Image.new("RGB", (W1, H1), "#0d1117")
d1 = ImageDraw.Draw(img1)

rows1 = [{"hdr": [(ML,"Day","#8b949e"),(145,"Input","#58a6ff"),(275,"Output","#3fb950"),(405,"Total","#d29922"),(520,"Calls","#8b949e")]}]
for day in days:
    v = daily[day]
    rows1.append({"cells": [(ML,day,"#c9d1d9"),(145,fmt(v["in"]),"#58a6ff"),(275,fmt(v["out"]),"#3fb950"),(405,fmt(v["total"]),"#d29922"),(520,str(v["calls"]),"#8b949e")], "bar_val": v["total"]})
tot1 = [(ML,"TOTAL","#f0f6fc"),(145,fmt(g_in),"#58a6ff"),(275,fmt(g_out),"#3fb950"),(405,fmt(g_total),"#d29922"),(520,str(g_calls),"#f0f6fc")]
draw_table(d1, MT, "Qwen 3.6-27B-FP8 - Token Usage by Day", rows1, tot1)
img1.save("/opt/data/scripts/token_stats_table.png", "PNG")
print("Table done")

# TABLE 2: Cost
nr2 = len(days) + 2
W2 = 750
H2 = MT + nr2 * RH + 40
img2 = Image.new("RGB", (W2, H2), "#0d1117")
d2 = ImageDraw.Draw(img2)
title2 = f"Cost Estimate ($0.20/$0.60 per 1M in/out) - ${g_cost:.2f} total"
d2.text((30, 8), title2, fill="#f97583", font=fontT)

y2 = MT
d2.rectangle([25, y2-16, W2-30, y2+6], fill="#161b22")
hdr2 = [(30,"Day","#8b949e"),(145,"In ($)", cant continue

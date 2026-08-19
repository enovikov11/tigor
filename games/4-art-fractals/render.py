#!/usr/bin/env python3
"""Fractals — Living Circles. Headless render via Pillow → PNG + GIF."""
import math, random, colorsys
from PIL import Image, ImageDraw

random.seed(42)
W, H = 1920, 1080
N = 60  # frames
DEPTH, BR = 5, 3
BA = math.atan2(84, -187)
NS = 0.0015

# HSB→RGB
def rgb(h, s, b):
    return colorsys.hsv_to_rgb(h/360, s/100, b/100)

def hrb(h, s, b):
    r, g, bl = rgb(h, s, b)
    return (int(r*255), int(g*255), int(bl*255))

# Palette: (H, S, B)
PAL = [(260,80,95),(290,85,90),(320,75,85),(340,80,95),
       (200,80,95),(180,85,90),(50,70,95),(350,75,90)]

# FBM via layered sin/cos (no dependency)
def fbm(x, y, t, o=4):
    v, a, f, s = 0, 1, 1, 0
    for _ in range(o):
        v += (math.sin(x*f+t*0.01+1.3)*math.cos(y*f+t*0.007+2.7)+1)*0.5*a
        s += a; a *= 0.5; f *= 2.1
    return v/s

# Build fractal tree at time t
def build(t):
    nodes = []
    cx = W/2 + math.sin(t*0.0002)*80
    cy = H/2 + math.cos(t*0.00015)*60
    r0 = min(W,H)*0.32 + math.sin(t*0.0003)*25
    line = [{"x":cx,"y":cy,"r":r0,"d":0,"s":0}]
    for d in range(DEPTH):
        nxt = []
        for n in line:
            nodes.append(n)
            ba = t*0.0004 + n["s"]
            for b in range(BR):
                wx = fbm(n["x"]*NS+1.7, n["y"]*NS+1.7, t, 3)
                wy = fbm(n["x"]*NS+3.1, n["y"]*NS+3.1, t, 3)
                warp = math.atan2(wy-0.5, wx-0.5)*0.3
                a = ba + b*BA + warp + math.sin(t*0.001+d*0.5)*0.2
                cr = n["r"]*0.7 if d==0 else n["r"]*(84/289)*2.5
                dist = n["r"]*(0.35 if d==0 else (1-84/289))
                nx, ny = n["x"]+math.sin(a)*dist, n["y"]+math.cos(a)*dist
                nr = cr*(0.8+fbm(nx*0.003, ny*0.003, t, 2)*0.4)
                nxt.append({"x":nx,"y":ny,"r":nr,"d":d+1,"s":n["s"]+b*1.37+d*0.73})
        line = nxt
    nodes.extend(line)
    return nodes

frames = []
for i in range(N):
    t = i * 50
    img = Image.new("RGB", (W,H), (5, 2, 15))
    draw = ImageDraw.Draw(img)
    nodes = build(t)

    # Rings (outer to inner for proper layering)
    for n in sorted(nodes, key=lambda n: -n["d"]):
        ci = n["d"] % len(PAL)
        h = (PAL[ci][0] + math.sin(t*0.0005+n["s"])*30) % 360
        sw = max(1, 4 - n["d"])
        al = max(0.15, 0.8 - n["d"]*0.1)
        r = max(1, int(n["r"]))
        c = hrb(h, PAL[ci][1], PAL[ci][2])
        # Glow: draw larger semi-transparent ellipse first
        for glow_r in range(3, 0, -1):
            ga = al * 0.08 * glow_r
            gc = (int(c[0]*ga), int(c[1]*ga), int(c[2]*ga))
            dr = r + glow_r*4
            draw.ellipse([n["x"]-dr, n["y"]-dr, n["x"]+dr, n["y"]+dr],
                         fill=gc)
        # Main ring
        draw.ellipse([n["x"]-r, n["y"]-r, n["x"]+r, n["y"]+r],
                     outline=(*c,), width=sw)

    # Tip dots
    for n in nodes:
        if n["d"] >= DEPTH-1:
            ci = n["d"] % len(PAL)
            al = 0.4 + math.sin(t*0.002+n["s"])*0.2
            dr = 3
            c = hrb(PAL[ci][0], PAL[ci][1], 100)
            fc = (int(c[0]*al*2), int(c[1]*al*2), int(c[2]*al*2))
            draw.ellipse([n["x"]-dr, n["y"]-dr, n["x"]+dr, n["y"]+dr], fill=fc)

    frames.append(img)
    if i % 15 == 0:
        print(f"Frame {i}/{N}")

frames[15].save("/home/hermes/games/4-art-fractals/preview.png")
gif = frames[::2]
gif[0].save("/home/hermes/games/4-art-fractals/fractals.gif",
    save_all=True, append_images=gif[1:],
    duration=100, loop=0)
print(f"Done — preview + {len(frames)}-frame GIF")

#!/usr/bin/env python3
"""The apps' own icons, which the App Installer needs in the zip (the scraper puts the game's cover over them):
app/soh/icon.png, an ocarina on a field by day, and app/2ship/icon.png, a moon over hills by night. 240x160, pixel art
drawn at 1/4 size and scaled up. Needs Pillow.
  tools/icons.py
"""
import math
from PIL import Image

W, H, S = 60, 40, 4


def canvas(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            px[x, y] = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
    return img, px


def put(px, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c


def hills(px, colors, base, amp, freq, phase):
    for x in range(W):
        top = int(base + amp * math.sin(x / freq + phase))
        for y in range(top, H):
            put(px, x, y, colors[(x + y) % 7 == 0])


def save(img, path):
    img.resize((W * S, H * S), Image.NEAREST).save(path, optimize=True)


# day: sky, two hills, an ocarina (body, mouthpiece, holes) over the grass
img, px = canvas((70, 132, 226), (150, 204, 246))
for cx, cy in ((9, 6), (37, 4)):
    for dx, dy, w in ((0, 1, 9), (2, 0, 5), (1, 2, 7)):
        for i in range(w):
            put(px, cx + dx + i, cy + dy, (250, 252, 255))
hills(px, ((96, 176, 80), (84, 160, 70)), 24, 3, 8.0, 0.4)
hills(px, ((70, 146, 58), (60, 132, 50)), 30, 2, 6.0, 2.0)
for y in range(14, 29):
    for x in range(17, 44):
        d = ((x - 30) / 13.0) ** 2 + ((y - 21) / 7.0) ** 2
        if d <= 1:
            put(px, x, y, (120, 182, 232) if d < 0.55 else (82, 140, 204))
for y in range(17, 22):
    for x in range(40, 47):
        put(px, x, y, (82, 140, 204) if y in (17, 21) else (120, 182, 232))
for x, y in ((24, 19), (28, 18), (32, 18), (36, 19), (27, 23), (33, 23)):
    put(px, x, y, (40, 70, 120))
for x in range(22, 36):
    put(px, x, 16, (200, 230, 252))
save(img, "app/soh/icon.png")

# night: sky, stars, a moon with craters, dark hills
img, px = canvas((20, 22, 60), (74, 56, 120))
for x, y in ((5, 4), (12, 9), (21, 3), (30, 7), (50, 3), (56, 10), (8, 15), (26, 13), (44, 16), (53, 18)):
    put(px, x, y, (255, 248, 210))
for y in range(4, 27):
    for x in range(22, 46):
        d = (x - 34) ** 2 + (y - 15) ** 2
        if d <= 110:
            put(px, x, y, (246, 226, 160) if d < 80 else (226, 200, 130))
for cx, cy, r in ((30, 12, 2), (38, 19, 3), (36, 10, 1), (29, 20, 1)):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(px, x, y, (210, 184, 118))
hills(px, ((44, 40, 82), (38, 34, 74)), 27, 3, 7.0, 1.1)
hills(px, ((26, 24, 52), (22, 20, 46)), 32, 2, 5.0, 2.6)
save(img, "app/2ship/icon.png")

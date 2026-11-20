#!/usr/bin/env python3
"""Draw "The World in One Day" — a broadsheet front page summing up
Friday 20 November 2026 — at 2048x2048, then Lanczos-downscale it to
the 1024x1024 entry.png the competition hands in.

The page is deliberately sparse: three hero stories with drawn
illustration panels, a dotted world map of the day's story places, a
markets strip, twelve one-line briefs and a footer. Legibility beat
density in the previous edition of this contest, so every headline is
measured with PIL's text metrics and shrunk or wrapped until it fits
its box, and the artwork stays bold and simple.
"""

import math

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- setup

W = 2048                      # drawn at 2x, downscaled to 1024
PAPER = (250, 247, 240)       # #faf7f0
INK = (18, 16, 14)
RED = (179, 0, 27)            # #b3001b
BAND = (236, 229, 214)        # markets strip shading
MUTE = (90, 84, 76)
SLATE = (70, 95, 125)         # slate blue: water, map dots, rain
OCHRE = (196, 138, 44)        # land and burst rings
PALE = (243, 239, 228)        # illustration panel tint
SMOKE = (158, 152, 142)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"

MARGIN = 92
CW = W - 2 * MARGIN           # content width

img = Image.new("RGB", (W, W), PAPER)
d = ImageDraw.Draw(img)


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(text, f):
    return d.textlength(text, font=f)


def wrap(text, f, max_w):
    """Greedy word wrap; returns the list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_single(text, path, start, max_w, min_size=20):
    """Largest size <= start at which text fits max_w on one line."""
    size = start
    while size > min_size and tw(text, font(path, size)) > max_w:
        size -= 2
    return font(path, size)


def draw_lines(x, y, lines, f, lh, fill=INK):
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def centered(text, y, f, fill=INK):
    d.text(((W - tw(text, f)) / 2, y), text, font=f, fill=fill)


def rule(y, height, fill=INK):
    d.rectangle([MARGIN, y, W - MARGIN, y + height], fill=fill)


# ---------------------------------------------------------------- masthead

title = "THE WORLD IN ONE DAY"
tf = fit_single(title, SERIF_B, 140, CW)
centered(title, 40, tf)
y = 40 + int(tf.size * 1.18)

rule(y + 4, 9)
y += 22
date_f = fit_single(
    "FRIDAY 20 NOVEMBER 2026 \u00b7 17 STORIES \u00b7 7 REGIONS \u00b7 ONE PAGE",
    SANS_B, 42, CW)
centered("FRIDAY 20 NOVEMBER 2026 \u00b7 17 STORIES \u00b7 7 REGIONS \u00b7 ONE PAGE",
         y, date_f, fill=RED)
y += int(date_f.size * 1.22)
rule(y, 3)
y += 24

# ------------------------------------------------------- hero artwork
# One flat illustration style throughout: bold PIL primitives, the page's
# own palette, shapes big enough to read at thumbnail size.

def panel(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PALE, outline=INK, width=4)


def burst(cx, cy, r):
    """An explosion starburst: radiating ink spikes, red heart, ochre ring."""
    for k in range(10):
        a = math.radians(k * 36 + 8)
        rr = r if k % 2 == 0 else int(r * 0.62)
        d.line([cx, cy, cx + rr * math.cos(a), cy + rr * math.sin(a)],
               fill=INK, width=7)
    d.ellipse([cx - r * 0.34, cy - r * 0.34, cx + r * 0.34, cy + r * 0.34],
              outline=OCHRE, width=7)
    d.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2],
              fill=RED)


def smoke(cx, cy, s):
    for dx, dy, r in ((-s, 6, int(s * 0.62)), (0, -6, int(s * 0.8)),
                      (s, 2, int(s * 0.66))):
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                  fill=SMOKE)


def trail(x0, y0, x1, y1, lift):
    """A dashed missile arc from (x0, y0) down to (x1, y1)."""
    pts = []
    for t in range(21):
        u = t / 20
        pts.append((x0 + (x1 - x0) * u,
                    y0 + (y1 - y0) * u - lift * 4 * u * (1 - u)))
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=INK, width=4)
    a = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    tip = pts[-1]
    d.polygon([(tip[0] + 16 * math.cos(a), tip[1] + 16 * math.sin(a)),
               (tip[0] + 10 * math.cos(a + 2.5), tip[1] + 10 * math.sin(a + 2.5)),
               (tip[0] + 10 * math.cos(a - 2.5), tip[1] + 10 * math.sin(a - 2.5))],
              fill=RED)


def art_kyiv(x, y, w, h):
    panel(x, y, w, h)
    # river band along the foot, slate under a wavy bank line
    bank = [(x, y + h - 52), (x + 130, y + h - 66), (x + 300, y + h - 50),
            (x + 460, y + h - 64), (x + w, y + h - 54), (x + w, y + h),
            (x, y + h)]
    d.polygon(bank, fill=SLATE)
    # suspension bridge: two towers, a deck, cables and hangers
    deck_y = y + h - 92
    tx1, tx2 = x + 168, x + 402
    for tx in (tx1, tx2):
        d.rectangle([tx - 11, y + 44, tx + 11, y + h - 40], fill=INK)
    d.line([x + 6, deck_y, x + w - 6, deck_y], fill=INK, width=10)
    spans = [(x + 6, tx1, deck_y, y + 44), (tx1, tx2, y + 44, y + 44),
             (tx2, x + w - 6, y + 44, deck_y)]
    for xa, xb, ya, yb in spans:
        mid = ((xa + xb) // 2, max(ya, yb) + 34)
        d.line([xa, ya, mid[0], mid[1]], fill=INK, width=5)
        d.line([mid[0], mid[1], xb, yb], fill=INK, width=5)
        for fx in range(xa + 34, xb - 10, 44):
            u = (fx - xa) / (xb - xa)
            top = (ya + (mid[1] - ya) * (u / 0.5)) if u < 0.5 else \
                  (mid[1] + (yb - mid[1]) * ((u - 0.5) / 0.5))
            d.line([fx, top, fx, deck_y], fill=INK, width=3)
    # smoke first (behind the bursts), then bursts and incoming trails
    smoke(x + 452, y + 34, 30)
    smoke(x + 128, y + 26, 24)
    burst(x + 470, y + 92, 42)
    burst(x + 118, y + 66, 32)
    trail(x + 40, y + 8, x + 104, y + 58, 26)
    trail(x + w - 30, y + 6, x + 484, y + 84, 30)


def art_cyclone(x, y, w, h):
    panel(x, y, w, h)
    # coastline: ochre land shoulder on the right
    coast = [(x + 408, y), (x + 452, y + 52), (x + 428, y + 116),
             (x + 492, y + 168), (x + 520, y + h), (x + w, y + h),
             (x + w, y)]
    d.polygon(coast, fill=(232, 205, 150))
    d.line(coast[:5], fill=INK, width=5)
    # cyclone: concentric broken arcs around an ink eye
    cx, cy = x + 218, y + h // 2
    for i, r in enumerate((30, 54, 78, 102)):
        start = 15 + i * 57
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + 235,
              fill=SLATE, width=12)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=INK)
    # diagonal rain streaks
    for rx, ry in ((36, 26), (96, 66), (52, 118), (140, 150), (330, 30),
                   (368, 84), (316, 150), (150, 18), (262, 160), (388, 140)):
        d.line([x + rx, y + ry, x + rx - 18, y + ry + 30], fill=SLATE, width=5)
    # two palms, bent by the wind
    for px, py, s in ((64, h - 14, 1.0), (492, h - 10, 0.8)):
        bx, by = x + px, y + py
        d.line([bx, by, bx + 10 * s, by - 52 * s], fill=INK, width=7)
        tx, ty = bx + 10 * s, by - 52 * s
        for a in (-165, -120, -75, -30, 15):
            ar = math.radians(a)
            d.arc([tx - 30 * s, ty - 14 * s, tx + 30 * s, ty + 16 * s],
                  a, a + 55, fill=INK, width=5)


def art_icj(x, y, w, h):
    panel(x, y, w, h)
    cx, cy = x + w // 2, y + h // 2 + 4
    # dotted globe behind the scales
    for k in range(40):
        a = math.radians(k * 9)
        dx, dy = cx + 76 * math.cos(a), cy + 76 * math.sin(a)
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=SLATE)
        ex, ey = cx + 34 * math.cos(a), cy + 76 * math.sin(a)
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=SLATE)
        gx, gy = cx + 76 * math.cos(a), cy + 26 * math.sin(a)
        d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=SLATE)
    # scales of justice
    top = y + 34
    d.line([cx, top + 16, cx, y + h - 34], fill=INK, width=8)
    d.ellipse([cx - 9, top - 4, cx + 9, top + 14], fill=RED)
    beam_y = top + 22
    d.line([cx - 118, beam_y, cx + 118, beam_y], fill=INK, width=8)
    for sx in (cx - 118, cx + 118):
        pan_y = beam_y + 58
        d.line([sx, beam_y, sx - 30, pan_y], fill=INK, width=4)
        d.line([sx, beam_y, sx + 30, pan_y], fill=INK, width=4)
        d.polygon([(sx - 38, pan_y), (sx + 38, pan_y), (sx + 22, pan_y + 17),
                   (sx - 22, pan_y + 17)], fill=INK)
    d.polygon([(cx - 34, y + h - 20), (cx + 34, y + h - 20),
               (cx + 20, y + h - 34), (cx - 20, y + h - 34)], fill=INK)
    # gavel, struck at the lower right
    gx, gy = x + w - 128, y + h - 44
    d.line([gx - 34, gy + 26, gx + 30, gy - 30], fill=INK, width=9)
    ca, sa = math.cos(math.radians(-40)), math.sin(math.radians(-40))
    hx, hy = gx + 38, gy - 38
    corners = []
    for lx, ly in ((-30, -11), (30, -11), (30, 11), (-30, 11)):
        corners.append((hx + lx * ca - ly * sa, hy + lx * sa + ly * ca))
    d.polygon(corners, fill=RED)
    d.line([gx + 52, gy + 8, gx + 96, gy + 8], fill=INK, width=6)


ART = [art_kyiv, art_cyclone, art_icj]

# ---------------------------------------------------------------- heroes

HEROES = [
    ("EUROPE",
     "Kyiv's bridges hit in Russia's heaviest strike of the month",
     "Ballistic missiles struck three bridges in the capital, killing eight "
     "and wounding 28 across nine regions; embassy windows and a cathedral "
     "were blown out."),
    ("ASIA",
     "Cyclone Akvan comes ashore in Odisha",
     "The storm made landfall with mass evacuations under way along India's "
     "east coast, the season's strongest system to reach the Bay of Bengal "
     "shore."),
    ("THE HAGUE",
     "World court: Myanmar committed genocide",
     "The ICJ ruled Myanmar's campaign against the Rohingya was genocide \u2014 "
     "the court's first such finding against a state. Refugees in Bangladesh "
     "welcomed the verdict."),
]

hero_top = y
col_gap = 46
col_w = (CW - 2 * col_gap) // 3
hero_bottom = hero_top
ART_H = 180

for i, (kicker, head, deck) in enumerate(HEROES):
    x = MARGIN + i * (col_w + col_gap)
    ART[i](x, hero_top, col_w, ART_H)
    cy = hero_top + ART_H + 14
    d.text((x, cy), kicker, font=font(SANS_B, 36), fill=RED)
    cy += 50
    hf = font(SERIF_B, 50)
    head_lines = wrap(head, hf, col_w)
    while len(head_lines) > 3 and hf.size > 34:
        hf = font(SERIF_B, hf.size - 3)
        head_lines = wrap(head, hf, col_w)
    cy = draw_lines(x, cy, head_lines, hf, int(hf.size * 1.2))
    cy += 10
    df = font(SERIF, 26)
    deck_lines = wrap(deck, df, col_w)
    cy = draw_lines(x, cy, deck_lines, df, 33, fill=(40, 36, 32))
    hero_bottom = max(hero_bottom, cy)

for i in (1, 2):
    dx = MARGIN + i * (col_w + col_gap) - col_gap // 2
    d.line([dx, hero_top + 4, dx, hero_bottom], fill=MUTE, width=2)

y = hero_bottom + 18
rule(y, 3)
y += 20

# ------------------------------------------------------------ world map
# A dotted-grid world map: land ranges on a 96 x 11 grid (3.75 degrees a
# column, 13 a row, from 74N), with red dots at the day's story places.

MAP_LAND = [
    [(12, 14), (17, 19), (22, 25), (28, 30), (38, 43), (58, 70), (74, 84),
     (88, 95)],
    [(3, 10), (13, 31), (40, 42), (44, 44), (50, 53), (55, 95)],
    [(13, 31), (45, 46), (47, 56), (57, 86), (89, 92)],
    [(15, 29), (44, 57), (58, 82), (84, 86)],
    [(19, 25), (42, 58), (59, 63), (65, 71), (73, 79)],
    [(26, 32), (43, 58), (67, 69), (73, 79), (81, 84)],
    [(27, 34), (44, 58), (75, 79), (81, 85), (86, 88)],
    [(28, 35), (50, 57), (59, 60), (78, 88)],
    [(28, 33), (51, 56), (78, 87), (92, 93)],
    [(28, 31), (91, 93)],
    [(28, 30)],
]
MAP_PLACES = [  # (lon, lat): Kyiv, Odisha, The Hague, Riyadh, Shenzhen,
    (30.5, 50.4), (86.0, 20.0), (4.3, 52.0), (46.7, 24.6), (114.0, 22.5),
    (-0.1, 51.5), (30.7, 36.9), (36.8, -1.3), (56.3, 26.6), (-77.0, 38.9),
]  # London, Antalya, Nairobi, Hormuz, Washington

map_pitch = 17
map_w = 96 * map_pitch
map_x = MARGIN + (CW - map_w) // 2
for row, ranges in enumerate(MAP_LAND):
    for c0, c1 in ranges:
        for c in range(c0, c1 + 1):
            cx = map_x + c * map_pitch + map_pitch // 2
            cy = y + row * map_pitch + map_pitch // 2
            d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=SLATE)
for lon, lat in MAP_PLACES:
    c = round((lon + 180) / 3.75)
    r = round((74 - lat) / 13)
    cx = map_x + c * map_pitch + map_pitch // 2
    cy = y + r * map_pitch + map_pitch // 2
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=PAPER)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED)
y += len(MAP_LAND) * map_pitch + 20

# ---------------------------------------------------------------- markets

MARKETS = [
    ("NIKKEI \u22124.8%", "Asia's AI sell-off deepens"),
    ("S&P 500", "fifth straight day of losses"),
    ("ANTHROPIC", "slides a day after its record IPO"),
    ("GTA VI", "launch sales top $2.3 billion"),
]

band_h = 134
d.rectangle([MARGIN, y, W - MARGIN, y + band_h], fill=BAND)
# a small red down-trend chart at the strip's left
chart = [(0, 26), (28, 42), (52, 34), (78, 62), (102, 54), (128, 88)]
cpts = [(MARGIN + 22 + px, y + py) for px, py in chart]
d.line(cpts, fill=RED, width=7, joint="curve")
for px, py in cpts[1:-1]:
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED)
hx, hy = cpts[-1]
d.polygon([(hx + 20, hy + 14), (hx - 4, hy + 12), (hx + 4, hy - 10)],
          fill=RED)
chart_w = 176
cell_w = (CW - chart_w) // 4
for i, (head, tail) in enumerate(MARKETS):
    cx = MARGIN + chart_w + i * cell_w
    hf = fit_single(head, SANS_B, 44, cell_w - 28)
    d.text((cx + (cell_w - tw(head, hf)) / 2, y + 20), head, font=hf, fill=INK)
    tf2 = font(SANS, 28)
    tail_lines = wrap(tail, tf2, cell_w - 36)
    ty = y + 68
    for line in tail_lines[:2]:
        d.text((cx + (cell_w - tw(line, tf2)) / 2, ty), line, font=tf2,
               fill=(52, 47, 40))
        ty += 30
    if i:
        d.line([cx, y + 14, cx, y + band_h - 14], fill=MUTE, width=2)
y += band_h + 24

# ---------------------------------------------------------------- briefs

BRIEFS = [
    ("EUROPE", "UK and EU seal their reset deal",
     "Youth mobility for up to 100,000 a year each way headlines the first "
     "post-Brexit settlement."),
    ("CLIMATE", "COP31 ends in deadlock",
     "Fossil fuels were scrubbed from the draft deal on the final day in "
     "Antalya; talks roll on."),
    ("DIPLOMACY", "Shenzhen declaration, day two",
     "Trump, Xi and Putin's peace declaration draws a seating-plan row and "
     "allied unease."),
    ("IRAN", "Trump delays his Iran decision",
     "'Not rushing,' the president says \u2014 no call on new strikes until "
     "the new year."),
    ("WASHINGTON", "Senate blocks war-powers bill",
     "The bid to force an end to the Iran war failed 51\u201348, its first "
     "post-midterms test."),
    ("MIDEAST", "Houthi missile hits Riyadh tower",
     "The PIF Tower lost windows across eight floors \u2014 the second attack "
     "on the district this month."),
    ("EUROPE", "Poland reports airspace violations",
     "Two Russian missiles and a drone crossed overnight as allied exercises "
     "began."),
    ("EUROPE", "Estonia shuts its Russian border",
     "The crossing closes for at least six months; Moscow promises a "
     "response."),
    ("UKRAINE", "Crimea Bridge struck a third time",
     "Rail traffic has resumed across the Kerch link after the week's latest "
     "strike."),
    ("SEA LANES", "Tanker ablaze in Hormuz",
     "A tanker burns in the strait that carries a fifth of the world's oil."),
    ("AFRICA", "Kenya's last Ebola patient goes home",
     "The discharge starts a 42-day countdown to an Ebola-free declaration."),
    ("SCIENCE", "Voyager 1 phones home",
     "NASA's probe is now one light-day from Earth \u2014 the farthest voice "
     "we have."),
]

FOOTER_TOP = W - 124
brief_gap = 58
bcol_w = (CW - brief_gap) // 2
rows = 6
row_h = (FOOTER_TOP - y) // rows

for idx, (region, head, deck) in enumerate(BRIEFS):
    col = idx // rows
    row = idx % rows
    x = MARGIN + col * (bcol_w + brief_gap)
    by = y + row * row_h
    # region tag and headline share one line
    rf = font(SANS_B, 30)
    d.text((x, by + 5), region, font=rf, fill=RED)
    rx = x + tw(region, rf) + 18
    hf = fit_single(head, SERIF_B, 38, x + bcol_w - rx, min_size=26)
    d.text((rx, by), head, font=hf, fill=INK)
    # deck below, up to two lines
    df = font(SERIF, 27)
    deck_lines = wrap(deck, df, bcol_w)
    draw_lines(x, by + 46, deck_lines[:2], df, 33, fill=(40, 36, 32))

# centre divider between the two brief columns
dx = MARGIN + bcol_w + brief_gap // 2
d.line([dx, y + 2, dx, FOOTER_TOP - 8], fill=MUTE, width=2)

# ---------------------------------------------------------------- footer

rule(FOOTER_TOP, 3)
foot = ("Plus: Van Gogh sells for a record $190.4M \u00b7 Georgia gas blast "
        "kills six \u00b7 North Korea expands uranium enrichment, IAEA warns "
        "\u00b7 Nigeria moves to end jail for attempted suicide \u00b7 "
        "Potatoes grown in lunar soil.")
ff = font(SERIF, 31)
foot_lines = wrap(foot, ff, CW)
fy = FOOTER_TOP + 16
for line in foot_lines[:2]:
    centered(line, fy, ff, fill=(40, 36, 32))
    fy += 38

# ---------------------------------------------------------------- save

img = img.resize((1024, 1024), Image.LANCZOS)
img.save("entry.png", optimize=True)
print("wrote entry.png")

#!/usr/bin/env python3
"""Draw "The World in One Day" — a broadsheet front page summing up
Friday 20 November 2026 — at 2048x2048, then Lanczos-downscale it to
the 1024x1024 entry.png the competition hands in.

The page is deliberately sparse: three hero stories, a markets strip,
twelve one-line briefs and a footer. Legibility beat density in the
previous edition of this contest, so every headline is measured with
PIL's text metrics and shrunk or wrapped until it fits its box.
"""

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- setup

W = 2048                      # drawn at 2x, downscaled to 1024
PAPER = (250, 247, 240)       # #faf7f0
INK = (18, 16, 14)
RED = (179, 0, 27)            # #b3001b
BAND = (236, 229, 214)        # markets strip shading
MUTE = (90, 84, 76)

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
tf = fit_single(title, SERIF_B, 158, CW)
centered(title, 52, tf)
y = 52 + int(tf.size * 1.18)

rule(y + 6, 10)
y += 26
date_f = fit_single(
    "FRIDAY 20 NOVEMBER 2026 \u00b7 17 STORIES \u00b7 7 REGIONS \u00b7 ONE PAGE",
    SANS_B, 46, CW)
centered("FRIDAY 20 NOVEMBER 2026 \u00b7 17 STORIES \u00b7 7 REGIONS \u00b7 ONE PAGE",
         y, date_f, fill=RED)
y += int(date_f.size * 1.25)
rule(y, 3)
y += 30

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

for i, (kicker, head, deck) in enumerate(HEROES):
    x = MARGIN + i * (col_w + col_gap)
    cy = hero_top
    d.text((x, cy), kicker, font=font(SANS_B, 40), fill=RED)
    cy += 56
    hf = font(SERIF_B, 60)
    head_lines = wrap(head, hf, col_w)
    while len(head_lines) > 3 and hf.size > 34:
        hf = font(SERIF_B, hf.size - 3)
        head_lines = wrap(head, hf, col_w)
    cy = draw_lines(x, cy, head_lines, hf, int(hf.size * 1.22))
    cy += 12
    df = font(SERIF, 35)
    deck_lines = wrap(deck, df, col_w)
    cy = draw_lines(x, cy, deck_lines, df, 46, fill=(40, 36, 32))
    hero_bottom = max(hero_bottom, cy)
    if i:
        dx = x - col_gap // 2
        d.line([dx, hero_top + 4, dx, hero_bottom], fill=MUTE, width=2)

y = hero_bottom + 20
rule(y, 3)
y += 22

# ---------------------------------------------------------------- markets

MARKETS = [
    ("NIKKEI \u22124.8%", "Asia's AI sell-off deepens"),
    ("S&P 500", "fifth straight day of losses"),
    ("ANTHROPIC", "slides a day after its record IPO"),
    ("GTA VI", "launch sales top $2.3 billion"),
]

band_h = 178
d.rectangle([MARGIN, y, W - MARGIN, y + band_h], fill=BAND)
cell_w = CW // 4
for i, (head, tail) in enumerate(MARKETS):
    cx = MARGIN + i * cell_w
    hf = fit_single(head, SANS_B, 47, cell_w - 28)
    d.text((cx + (cell_w - tw(head, hf)) / 2, y + 26), head, font=hf, fill=INK)
    tf2 = font(SANS, 33)
    tail_lines = wrap(tail, tf2, cell_w - 36)
    ty = y + 92
    for line in tail_lines[:2]:
        d.text((cx + (cell_w - tw(line, tf2)) / 2, ty), line, font=tf2,
               fill=(52, 47, 40))
        ty += 40
    if i:
        d.line([cx, y + 18, cx, y + band_h - 18], fill=MUTE, width=2)
y += band_h + 30

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

FOOTER_TOP = W - 168
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
    rf = font(SANS_B, 33)
    d.text((x, by + 5), region, font=rf, fill=RED)
    rx = x + tw(region, rf) + 18
    hf = fit_single(head, SERIF_B, 41, x + bcol_w - rx, min_size=28)
    d.text((rx, by), head, font=hf, fill=INK)
    # deck below, up to two lines
    df = font(SERIF, 33)
    deck_lines = wrap(deck, df, bcol_w)
    draw_lines(x, by + 54, deck_lines[:2], df, 41, fill=(40, 36, 32))

# centre divider between the two brief columns
dx = MARGIN + bcol_w + brief_gap // 2
d.line([dx, y + 2, dx, FOOTER_TOP - 8], fill=MUTE, width=2)

# ---------------------------------------------------------------- footer

rule(FOOTER_TOP, 3)
foot = ("Plus: Van Gogh sells for a record $190.4M \u00b7 Georgia gas blast "
        "kills six \u00b7 North Korea expands uranium enrichment, IAEA warns "
        "\u00b7 Nigeria moves to end jail for attempted suicide \u00b7 "
        "Potatoes grown in lunar soil.")
ff = font(SERIF, 34)
foot_lines = wrap(foot, ff, CW)
fy = FOOTER_TOP + 22
for line in foot_lines[:2]:
    centered(line, fy, ff, fill=(40, 36, 32))
    fy += 44

# ---------------------------------------------------------------- save

img = img.resize((1024, 1024), Image.LANCZOS)
img.save("entry.png", optimize=True)
print("wrote entry.png")

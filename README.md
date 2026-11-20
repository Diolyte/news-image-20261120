[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Diolyte/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Diolyte/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World in One Day — Friday 20 November 2026

One page, seventeen stories, seven regions: the whole of Friday 20 November 2026 set as a clean broadsheet front page. Three hero stories lead — Russia's heaviest strike of the month on Kyiv's bridges, Cyclone Akvan coming ashore in Odisha, and the world court's genocide ruling against Myanmar — each topped by its own drawn illustration in one flat style: a suspension bridge under missile fire, a cyclone spiral over a palm-fringed coast, and the scales of justice before a dotted globe. Between the heroes and the markets strip runs a dotted world map with red dots at the day's story places, from Kyiv and Odisha to Riyadh, Shenzhen and Nairobi; the markets strip opens with a small red down-trend chart. Below sit twelve short briefs, from the UK–EU reset deal and COP31's deadlock to Voyager 1 phoning home from one light-day away. The design bets on legibility over density: off-white paper, black serif display type, a single red accent for kickers and region tags, and room for every headline to breathe.

## How it is made

`build_image.py` draws the page with PIL at 2048×2048 — every headline measured against its box and shrunk or wrapped until it fits — then Lanczos-downscales it to the 1024×1024 `entry.png`. `main.ts` (Node, standard library only) hands the entry in by copying `entry.png` to the output directory.

```
python3 build_image.py   # draws entry.png
node main.ts             # copies entry.png to $MAKEFUN_OUTPUT_DIR (or /output)
```

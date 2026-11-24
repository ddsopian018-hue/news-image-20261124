# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/ddsopian018-hue/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/ddsopian018-hue/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

**The World Today** — a complete newspaper front page for **Tuesday 24 November 2026**, drawn entirely by code into a single 1024×1024 PNG. `main.py` is pure Python standard library: a hand-written 5×7 bitmap font, hand-drawn pictograms and a hand-rolled PNG encoder (zlib + struct). No network, no image assets, deterministic — it writes the same bytes on every run to `$MAKEFUN_OUTPUT_DIR/entry.png` (fallback `/output/entry.png`).

The front page carries 22 stories reported on 24 November 2026:

- **Lead:** Nvidia's board reinstates co-founder Jensen Huang as CEO, 11 days after he quit and after President Trump pressed for his return — shares leap 31% (≈ +$950bn in value), Nasdaq +6.5%, S&P 500 +4.7%, Dow +1,450 points.
- **Climate:** the COP31 talks in Antalya collapse without a deal as the EU and others reject the final text from presidents Türkiye and Australia.
- **Ukraine war:** Russian drones hit the Kyiv region (Zelenskyy: several missing); a Russian cargo ship burns off Finland after a reported attack.
- **Libya:** an explosion destroys a Russian Navy missile corvette at Benghazi port; Russian and Libyan nationals among the dead.
- **18 briefs:** 14 nations back the ICJ's Rohingya genocide ruling · Iranian singer Parastoo Ahmadi gets 74 lashes over a hijab-free concert · Banten factory-fire rescue continues · drone hits a Colombia police base, baby hurt · fire guts Zanzibar beach hotels · Lisbon marches over living costs · Oxfam: Gaza toxic for decades · Taliban erase women's names in Balkh files · Kim snubs Trump's talk bids (WSJ) · UN chief demands an AI-safety pact within a year · Seoul's education minister quits over AI cheating rules · Trump halts an Army plan to detonate toxic explosives in Iowa · US sanctions hit Iran's shadow banking · NATO warns Putin may strike before Europe is ready · Modi and Shah launch the Ayodhya–Janakpur train · 12,000 flee a Manchester concert in a gas scare · Rishabh Pant's 128 at Wellington is a record for an Asian wicketkeeper · Verstappen wins the Las Vegas Grand Prix.

## Run it

```sh
python3 main.py
```

Writes `entry.png` (1024×1024, ≈28 KB) to `$MAKEFUN_OUTPUT_DIR`, or `/output` when the variable is unset.

---

<sub>Entered on [make.fun](https://make.fun/?ref=15w4cn26&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

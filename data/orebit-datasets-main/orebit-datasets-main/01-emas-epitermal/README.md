# 01 — Epithermal Gold Vein (synthetic)

Fictional prospect **"Cikaruncang"**. Modelled on the low-sulphidation
epithermal vein systems of the Sunda arc in West Java (Pongkor, Cikotok as
style analogues). No real data.

## The deposit

A single steeply dipping quartz vein in an andesitic volcanic host.

- **Strike** 340°, **dip** 75° toward 070° (ENE)
- **Strike length** ~900 m, tested ~380 m down dip, subcropping under cover
- **Vein thickness** 1–16 m with strong pinch-and-swell, mean ≈ 5 m
- **Three ore shoots** plunging ~45° within the vein plane — grade is not
  evenly distributed along strike, which is the whole reason this style is
  hard to estimate
- Silicic vein core, adularia–sericite selvage, argillic then propylitic halo
- Hydrothermal breccia along vein margins where the vein swells past ~8.5 m

## The drilling

103 angled holes for **20,187 m**, drilled from the hangingwall side on
sections 30 m apart, up to four holes per section testing progressively deeper
down-dip positions.

- Azimuth ≈ 250°, dip 48–68° (positive down)
- Downhole survey every 30 m with realistic azimuth walk and dip flattening
- Traces desurveyed by **minimum curvature**, then the geological model is
  evaluated along the actual drifted trace — so collar, survey and assay are
  internally consistent
- **99 of 103 holes cut the vein.** The four misses are real misses, not errors
- Median downhole vein intersection **7.5 m** (2.0–19.5 m)

## Files

**collar.csv** — 103 rows
| Column | Unit | Notes |
|---|---|---|
| BHID | | `CKR-001` … `CKR-103` |
| XCOLLAR, YCOLLAR | m | UTM 48S, WGS 84 (West Java) |
| ZCOLLAR | m | elevation, positive up (750–1002 m) |
| TD | m | total depth, 45–409 m |

**survey.csv** — 828 rows · `BHID, AT, AZ, DIP` — AT in metres, AZ 0–360°,
DIP **positive downward** (90 = vertical down).

**assay.csv** — 11,526 rows
| Column | Unit | Notes |
|---|---|---|
| FROM, TO | m | 1.0 m through the vein zone, 2.0 m elsewhere |
| AU_GPT | g/t | detection limit 0.01, below-DL reported as 0.005 |
| AG_GPT | g/t | detection limit 0.5, below-DL reported as 0.25 |
| SG | | bulk density, 2.33–2.76 |

**litho.csv** — 994 rows · `BHID, FROM, TO, LITH, ALT`

| LITH | | ALT | |
|---|---|---|---|
| `VN` | quartz vein | `SIL` | silicic |
| `BX` | hydrothermal breccia | `ADL` | adularia–sericite |
| `STK` | stockwork halo | `ARG` | argillic |
| `AND` | andesite | `PROP` | propylitic |
| `TUF` | lapilli tuff | `FRESH` | unaltered |

## Statistics

**In vein (`VN` + `BX`), n = 652**

| | Au (g/t) |
|---|---|
| Mean | 5.94 |
| Median | 2.63 |
| Maximum | 75.0 |
| **CV** | **1.66** |

Median Ag:Au ratio **12.2** — consistent with low-sulphidation systems.
Median gram·metre accumulation per hole: **16.5 g/t·m**.

**All samples, n = 11,423 assayed**: mean 0.428 g/t, median 0.019 g/t.
P90 0.19 · P99 9.35 · P99.9 47.1 g/t.

## What this one is good for

- **Top-cut / capping decisions.** CV 1.66 with a 75 g/t maximum against a
  2.6 g/t median is exactly the situation where capping changes the answer.
- **Domaining.** The vein has to be separated from the halo and the wall rock
  before any statistics mean anything. `litho.csv` gives you the truth to
  check your domain against.
- **True width vs downhole width.** Holes cut the vein obliquely. Estimating
  on downhole width overstates thickness.
- **Below-detection handling.** 11.9% of samples sit at half detection limit.
- **Short-range, high-nugget variography.** ~45% nugget, ~25 m range.
  A naive omnidirectional variogram will look like pure nugget.

## Regenerate

```bash
python3 ../_generator/gen_emas.py
```
Seed `20260829`. Change it for a different vein with the same character.

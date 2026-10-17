# 03 — Alluvial Tin Placer (synthetic)

Fictional block **"Sungai Berumput"**. Modelled on the cassiterite placers of
Bangka–Belitung and the traditional *bor Banka* drilling used to evaluate them.
No real data.

## The deposit

A buried palaeochannel. The tin is not in the sediment generally — it is
concentrated in a thin gravel layer sitting directly on bedrock, because that
is where dense cassiterite settles.

Profile from surface down:

| Layer | Code | Character |
|---|---|---|
| Overburden soil / clay | `TOP` | 0.8–4.5 m, barren |
| Alluvial sand | `PSR` | variable, trace Sn |
| Alluvial clay | `LMP` | variable, trace Sn |
| **Kaksa** — basal tin gravel | `KAK` | median 1.0 m, up to 4.0 m — the ore |
| Kong — kaolinised granite | `KONG` | bedrock, drilled 1–1.8 m |

Built into the model:

- **A meandering palaeochannel** incised into bedrock. Depth to bedrock runs
  ~5 m on the interfluves to **21 m in the thalweg**. Find the channel and you
  have found the ore; the whole exploration problem is a topographic one.
- **Kaksa thickens toward the channel axis** — from nothing on the flanks to
  4 m in the deepest ground.
- **Grade increases downward within the kaksa.** Cassiterite is densest at the
  very base, right on bedrock. The bottom sample is usually the best one.
- **A pay streak follows the channel axis**, with along-channel richer and
  poorer runs, so grade is not uniform even within the thalweg.
- A little cassiterite leaks into the base of the overlying alluvium and the
  weathered top of the granite — real placer boundaries are not knife-sharp.

## The drilling

500 vertical holes for **5,867 m** on a classic placer pattern:
**lines 100 m apart, holes every 25 m along line**, across a 604 × 1,906 m block.

- Close spacing along line, wide spacing between lines — the anisotropic
  sampling pattern placer work always produces
- 1.0 m samples from surface to total depth
- **26 holes are blocked** (*bor buntu*) and stopped before reaching bedrock.
  A hole that never reached bedrock never tested the kaksa, and treating it as
  a zero-grade hole is a real and expensive mistake
- **393 of 500 holes intersect kaksa**; the rest sit on bedrock highs outside
  the channel

## Files

**collar.csv** — 500 rows · `BHID, XCOLLAR, YCOLLAR, ZCOLLAR, TD`
`SBR-01-050` … `SBR-20-650` (line number, then station).
UTM 48S, WGS 84 (Bangka). Elevation 8–33 m. TD 2.0–22.5 m, median 11.0 m.

**survey.csv** — 1,000 rows. Two records per hole, AZ 0 / DIP 90 (vertical).

**assay.csv** — 5,990 rows, 1.0 m intervals

| Column | Unit | Notes |
|---|---|---|
| SN_KGM3 | kg/m³ | tin metal per cubic metre — the Indonesian placer convention, **not** ppm or % |
| BD_TM3 | t/m³ | in-situ bulk density: 1.55 topsoil, 1.72 alluvium, 1.94 kaksa, 2.05 bedrock |

Detection limit 0.005 kg/m³; below-DL values reported as 0.002.

**litho.csv** — 1,853 rows · `BHID, FROM, TO, LITH` with `TOP`, `PSR`, `LMP`,
`KAK`, `KONG`.

## Statistics

**Kaksa only, n = 664**

| | Sn (kg/m³) |
|---|---|
| Mean | 0.731 |
| Median | 0.405 |
| Maximum | 9.74 |
| **CV** | **1.42** |

Only 8 samples (1.2%) exceed 5 kg/m³. Median accumulation per hole
**0.39 kg/m²**, maximum 18.4 kg/m².

All samples, n = 5,990: mean 0.093 kg/m³, median 0.002 kg/m³ — because most of
the ground is barren overburden. Reporting a global mean grade here is
meaningless, which is the lesson.

## What this one is good for

- **Grade × thickness, not grade.** The ore is a thin sheet. The quantity that
  matters is accumulation (kg/m²), and estimating grade and thickness
  separately gives a different answer than estimating their product.
- **2D / surface estimation.** A basal placer is naturally a 2D problem, not a
  3D block model. It is the standard counter-example to "always build a block
  model".
- **Bedrock surface modelling.** Interpolating the palaeochannel floor from
  the collars is a genuine exercise, and it controls everything else.
- **Anisotropic sample spacing.** 25 m along line against 100 m between lines
  — variography and declustering both have to respect that.
- **Handling incomplete holes.** The 26 blocked holes must be excluded or
  flagged, not read as barren.
- **Volume-basis grades.** kg/m³ does not composite the way g/t does. Density
  weighting that is correct for the gold dataset is wrong here.

## Regenerate

```bash
python3 ../_generator/gen_timah.py
```
Seed `20260831`.

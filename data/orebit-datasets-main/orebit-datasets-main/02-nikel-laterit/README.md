# 02 — Nickel Laterite (synthetic)

Fictional block **"Lamonto"**. Modelled on the nickel laterite profiles
developed over ultramafic bedrock in Southeast Sulawesi and Halmahera
(Sorowako, Pomalaa, Weda Bay as style analogues). No real data.

## The deposit

A weathering profile, not an intrusion. Everything about the data follows from
that: the geology is layered and sub-horizontal, thickness is controlled by
topography, and grade varies smoothly.

Profile from surface down:

| Horizon | Code | Thickness | Character |
|---|---|---|---|
| Ferricrete / iron cap | `OVB` | 0.3–3 m | Fe ~49%, Ni <0.9%, waste |
| Limonite | `LIM` | mean 7.9 m | Ni ~1.2%, Fe ~42%, MgO ~4% — Co ore |
| Saprolite | `SAP` | mean 11.7 m | Ni ~1.7%, Fe ~15%, MgO ~18% — Ni ore |
| Bedrock (peridotite) | `BRK` | drilled 2–3.5 m | Ni ~0.3%, MgO ~37% |

Built into the model:

- **Laterite thickness tracks slope.** Thick on gentle crests where the
  profile is preserved, thin on steep slopes where it has been stripped.
  Topography and thickness are genuinely linked, not independent noise.
- **Fe and MgO are strongly anti-correlated (r = −0.88).** Fe falls and MgO
  rises down the profile as serpentine survives and iron oxides are left
  behind. Everything else follows the same logic.
- **Nickel peaks in the upper saprolite** and declines toward bedrock — the
  classic supergene enrichment position, not the top of the hole.
- **A thin cobalt spike at the limonite/saprolite boundary**, the manganese
  oxide horizon. Co in limonite averages 0.119% against 0.051% in saprolite.
- **Extreme anisotropy.** Grade continuity runs ~170 m laterally against a few
  metres vertically. Any isotropic search ellipse gets this badly wrong.

## The drilling

350 vertical holes for **8,195 m**.

- **100 m regional grid**, with a **50 m infill block** in the centre
  (X 700–1100, Y 600–1000 local) — a realistic staged programme, and a
  built-in exercise in clustered sampling
- Collars scatter ~1.6 m from the planned grid node, as they do in the field
- 1.0 m samples from surface to total depth
- Holes stop 2–3.5 m into fresh bedrock; **8 holes were abandoned** in
  saprolite without reaching it

## Files

**collar.csv** — 350 rows · `BHID, XCOLLAR, YCOLLAR, ZCOLLAR, TD`
`LMT-0001` … `LMT-0350`. UTM 51S, WGS 84 (Southeast Sulawesi).
Elevation 241–396 m. TD 5.8–43.0 m, median 23.2 m.

**survey.csv** — 700 rows. Two records per hole, AZ 0 / DIP 90 (vertical).

**assay.csv** — 8,278 rows, 1.0 m intervals

| Column | Unit | Saprolite mean | Limonite mean |
|---|---|---|---|
| NI_PCT | % | 1.72 | 1.19 |
| CO_PCT | % | 0.051 | 0.119 |
| FE_PCT | % Fe elemental | 15.1 | 42.1 |
| MGO_PCT | % | 18.1 | 3.8 |
| SIO2_PCT | % | 36.2 | 12.0 |
| AL2O3_PCT | % | ~1.7 | ~5.0 |
| CR2O3_PCT | % | ~1.2 | ~2.3 |
| SG | | 1.65 | 1.46 |

41 intervals have all assays blank (lost sample). Oxide totals sum to ~82%;
the balance is loss on ignition, which is not reported — as in most real
laterite databases.

**litho.csv** — 1,366 rows · `BHID, FROM, TO, LITH` with `OVB`, `LIM`, `SAP`,
`BRK`.

## Statistics

All samples, n = 8,247 assayed: Ni mean **1.31%**, median 1.28%, max 3.62%,
**CV 0.47**.

Saprolite only, n = 4,085: Ni mean **1.72%**, median 1.67%, **CV 0.28**.
63.1% of saprolite samples are at or above a 1.5% Ni cut-off.
Median SiO₂/MgO ratio in saprolite **2.03**.

That CV of 0.28 is the headline. This is about as well-behaved as grade data
gets, and it is a completely different estimation problem from the gold.

## What this one is good for

- **Anisotropic search and variography.** Get the ratio wrong and the model
  smears grade vertically through horizons that do not connect.
- **Declustering.** The 50 m infill block over a 100 m grid biases naive
  global statistics upward. This is the cleanest teaching example of it.
- **Horizon-based domaining.** Estimating across the limonite/saprolite
  boundary is the classic laterite mistake — Fe and MgO make it obvious.
- **Multivariate work.** Seven correlated elements with real geochemical
  structure: Fe–MgO regression, SiO₂/MgO classification, Co–Mn association.
- **Density by horizon.** SG ranges 1.46 to 2.6. A single global density
  produces a badly wrong tonnage.

## Regenerate

```bash
python3 ../_generator/gen_nikel.py
```
Seed `20260830`.

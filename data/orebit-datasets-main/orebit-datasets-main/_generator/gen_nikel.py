"""
gen_nikel.py - dataset sintetis NIKEL LATERIT.
Analog gaya endapan: laterit atas ultramafik, Sulawesi Tenggara / Halmahera.
Blok FIKTIF "Lamonto". Semua angka dihasilkan model, bukan data nyata.

Karakter yang sengaja dibangun:
  - profil berlapis mendatar: tudung besi - limonit - saprolit - bedrock
  - bor vertikal pada grid teratur (100 m regional + sisipan 50 m)
  - ketebalan laterit dikontrol kemiringan lereng (tebal di punggungan landai,
    tipis di lereng curam) dan permukaan bedrock yang bergelombang
  - Ni memuncak di saprolit atas; Fe dan MgO berkorelasi negatif kuat
  - Co memuncak tipis di batas limonit/saprolit (horizon oksida Mn)
  - anisotropi ekstrem: kontinuitas lateral ratusan meter, vertikal beberapa meter
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SmoothNoise

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "02-nikel-laterit")
SEED = 20260830
rng = np.random.default_rng(SEED)

X0, Y0 = 392000.0, 9558000.0          # UTM 51S, Sulawesi Tenggara (fiktif)
EX, EY = 1900.0, 1500.0

# ------------------------------------------------------------------ medan
topo_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 560, 2, 2)
brk_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 300, 3, 2)
lim_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 380, 3, 2)
sap_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 340, 3, 2)
rich_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 430, 2, 2)

# noise 3D anisotropik: range horizontal ~170 m, vertikal ~4 m (rasio 42)
ANIS = 42.0
g3 = SmoothNoise(rng, (0, 0, -1500), (EX + 400, EY + 400, 3000), 170, 2, 3)


def topo(x, y):
    """Perbukitan laterit, elevasi ~190-430 m."""
    return 300.0 + 34.0 * topo_n(x, y) + 0.011 * y - 0.006 * x


def slope_pct(x, y, h=25.0):
    """Kemiringan lereng lokal (%) dari beda tinggi."""
    dzx = (topo(x + h, y) - topo(x - h, y)) / (2 * h)
    dzy = (topo(x, y + h) - topo(x, y - h)) / (2 * h)
    return 100.0 * np.sqrt(dzx ** 2 + dzy ** 2)


def profile(x, y):
    """Ketebalan tiap horizon (m) di posisi (x, y)."""
    sl = slope_pct(x, y)
    # laterit berkembang tebal di lereng landai, terkikis di lereng curam
    dev = np.clip(1.30 - 0.021 * sl, 0.40, 1.30)
    t_ovb = np.clip(1.3 + 0.55 * brk_n(x, y), 0.3, 3.0)
    t_lim = np.clip((8.1 + 3.6 * lim_n(x, y)) * dev, 0.8, 19.0)
    t_sap = np.clip((13.6 + 5.6 * sap_n(x, y)) * dev, 1.0, 28.0)
    return t_ovb, t_lim, t_sap, dev


# komposisi ujung tiap horizon: (Ni, Co, Fe, MgO, SiO2, Al2O3, Cr2O3, SG)
# baris = awal horizon (atas) dan akhir horizon (bawah)
ENDS = {
    "OVB": ((0.52, 0.030, 50.5, 0.50, 2.6, 8.2, 2.95, 1.55),
            (0.86, 0.055, 48.5, 1.10, 5.2, 7.0, 2.70, 1.55)),
    "LIM": ((0.92, 0.062, 47.0, 1.40, 6.5, 6.6, 2.60, 1.42),
            (1.38, 0.105, 37.5, 6.20, 17.5, 3.4, 1.95, 1.52)),
    "SAP": ((2.35, 0.055, 21.0, 9.5, 32.0, 2.4, 1.55, 1.48),
            (1.05, 0.022, 9.5, 27.5, 41.5, 1.0, 0.85, 1.85)),
    "BRK": ((0.30, 0.014, 6.8, 36.5, 40.0, 1.0, 0.48, 2.62),
            (0.26, 0.012, 6.2, 39.5, 41.0, 0.8, 0.42, 2.68)),
}
ELEM = ["NI", "CO", "FE", "MGO", "SIO2", "AL2O3", "CR2O3", "SG"]
# simpangan relatif tiap unsur (koefisien variasi lokal)
RELSD = dict(NI=0.13, CO=0.22, FE=0.07, MGO=0.11, SIO2=0.08,
             AL2O3=0.18, CR2O3=0.15, SG=0.06)

rows_col, rows_sur, rows_asy, rows_lit = [], [], [], []

# --- grid bor: regional 100 m + sisipan 50 m di blok tengah
nodes = set()
for gx in np.arange(50.0, EX, 100.0):
    for gy in np.arange(50.0, EY, 100.0):
        nodes.add((round(gx, 1), round(gy, 1)))
for gx in np.arange(700.0, 1101.0, 50.0):
    for gy in np.arange(600.0, 1001.0, 50.0):
        nodes.add((round(gx, 1), round(gy, 1)))
nodes = sorted(nodes, key=lambda p: (p[1], p[0]))

for i, (gx, gy) in enumerate(nodes, start=1):
    bhid = "LMT-%04d" % i
    # posisi lapangan meleset sedikit dari titik grid rencana
    x = gx + rng.normal(0, 1.6)
    y = gy + rng.normal(0, 1.6)
    xa, ya = np.array([x]), np.array([y])
    z = float(topo(xa, ya)[0])
    t_ovb, t_lim, t_sap, dev = [float(v[0]) for v in profile(xa, ya)]

    b_ovb = t_ovb
    b_lim = b_ovb + t_lim
    b_sap = b_lim + t_sap
    into_brk = rng.uniform(2.0, 3.5)
    TD = b_sap + into_brk

    # ~2% lubang gagal tembus bedrock (runtuh / bongkah), dihentikan lebih awal
    aborted = rng.random() < 0.02
    if aborted:
        TD = b_lim + rng.uniform(0.3, 0.8) * t_sap
    TD = float(np.round(TD, 1))

    rows_col.append((bhid, X0 + x, Y0 + y, z, TD))
    rows_sur.append((bhid, 0.0, 0.0, 90.0))
    rows_sur.append((bhid, TD, 0.0, 90.0))

    # --- sampel 1 m
    edges = np.arange(0.0, TD + 1e-6, 1.0)
    if edges[-1] < TD - 1e-6:
        edges = np.append(edges, TD)
    if edges.size > 2 and edges[-1] - edges[-2] < 0.3:
        edges = np.delete(edges, -2)          # gabung sisa pendek
    f = edges[:-1]
    t = edges[1:]
    mid = (f + t) / 2.0

    unit = np.where(mid < b_ovb, "OVB",
                    np.where(mid < b_lim, "LIM",
                             np.where(mid < b_sap, "SAP", "BRK")))
    # posisi relatif di dalam horizon (0 = atas, 1 = bawah)
    rel = np.zeros_like(mid)
    rel = np.where(unit == "OVB", mid / max(b_ovb, 1e-6), rel)
    rel = np.where(unit == "LIM", (mid - b_ovb) / max(t_lim, 1e-6), rel)
    rel = np.where(unit == "SAP", (mid - b_lim) / max(t_sap, 1e-6), rel)
    rel = np.where(unit == "BRK", np.clip((mid - b_sap) / 5.0, 0, 1), rel)
    rel = np.clip(rel, 0.0, 1.0)

    xs = np.full(mid.size, x)
    ys = np.full(mid.size, y)
    zs = z - mid
    n3 = g3(xs, ys, zs * ANIS)              # noise berkorelasi spasial
    rich = float(rich_n(xa, ya)[0])          # kekayaan blok skala ratusan meter

    vals = {}
    for k, e in enumerate(ELEM):
        lo = np.array([ENDS[u][0][k] for u in unit])
        hi = np.array([ENDS[u][1][k] for u in unit])
        base = lo + (hi - lo) * rel
        if e == "NI":
            # Ni memuncak di saprolit atas; blok kaya/miskin skala luas
            base = base * (1.0 + 0.13 * rich)
        noise = 1.0 + RELSD[e] * (0.72 * n3 + 0.69 * rng.standard_normal(mid.size))
        vals[e] = np.clip(base * noise, 0.0, None)

    # horizon oksida Mn: puncak Co tipis di batas limonit/saprolit
    co_spike = 1.0 + 1.9 * np.exp(-0.5 * ((mid - b_lim) / 1.3) ** 2)
    vals["CO"] = vals["CO"] * co_spike

    # batas atas fisik yang wajar
    vals["FE"] = np.clip(vals["FE"], 3.0, 56.0)
    vals["MGO"] = np.clip(vals["MGO"], 0.2, 45.0)
    vals["NI"] = np.clip(vals["NI"], 0.02, 4.5)
    vals["SG"] = np.clip(vals["SG"], 1.15, 2.85)

    lost = rng.random(mid.size) < 0.004      # ~0.4% sampel hilang
    for j in range(mid.size):
        if lost[j]:
            rows_asy.append((bhid, f[j], t[j], np.nan, np.nan, np.nan,
                             np.nan, np.nan, np.nan, np.nan, vals["SG"][j]))
        else:
            rows_asy.append((bhid, f[j], t[j], vals["NI"][j], vals["CO"][j],
                             vals["FE"][j], vals["MGO"][j], vals["SIO2"][j],
                             vals["AL2O3"][j], vals["CR2O3"][j], vals["SG"][j]))

    # --- log litologi (gabung run)
    b = 0
    for j in range(1, mid.size + 1):
        end = j == mid.size
        if end or unit[j] != unit[b]:
            rows_lit.append((bhid, float(f[b]), float(t[j - 1]), str(unit[b])))
            b = j

col = pd.DataFrame(rows_col, columns=["BHID", "XCOLLAR", "YCOLLAR", "ZCOLLAR", "TD"])
sur = pd.DataFrame(rows_sur, columns=["BHID", "AT", "AZ", "DIP"])
asy = pd.DataFrame(rows_asy, columns=["BHID", "FROM", "TO", "NI_PCT", "CO_PCT",
                                      "FE_PCT", "MGO_PCT", "SIO2_PCT",
                                      "AL2O3_PCT", "CR2O3_PCT", "SG"])
lit = pd.DataFrame(rows_lit, columns=["BHID", "FROM", "TO", "LITH"])

for c, nd in dict(XCOLLAR=2, YCOLLAR=2, ZCOLLAR=2, TD=1).items():
    col[c] = col[c].round(nd)
for c, nd in dict(AT=1, AZ=1, DIP=1).items():
    sur[c] = sur[c].round(nd)
rnd = dict(FROM=2, TO=2, NI_PCT=3, CO_PCT=4, FE_PCT=2, MGO_PCT=2,
           SIO2_PCT=2, AL2O3_PCT=2, CR2O3_PCT=3, SG=2)
for c, nd in rnd.items():
    asy[c] = asy[c].round(nd)
for c in ("FROM", "TO"):
    lit[c] = lit[c].round(2)

os.makedirs(OUT, exist_ok=True)
col.to_csv(os.path.join(OUT, "collar.csv"), index=False)
sur.to_csv(os.path.join(OUT, "survey.csv"), index=False)
asy.to_csv(os.path.join(OUT, "assay.csv"), index=False)
lit.to_csv(os.path.join(OUT, "litho.csv"), index=False)

m = asy.merge(lit, on="BHID")
m = m[(m.FROM_x >= m.FROM_y) & (m.TO_x <= m.TO_y)]
print("lubang     :", len(col), "| meter bor:", round(col.TD.sum()))
print("assay      :", len(asy), "| kosong:", int(asy.NI_PCT.isna().sum()))
print("TD  min/med/max:", col.TD.min(), col.TD.median(), col.TD.max())
print()
for u in ["OVB", "LIM", "SAP", "BRK"]:
    s = m[m.LITH == u]
    print("%-4s n=%5d  Ni=%.2f  Co=%.3f  Fe=%.1f  MgO=%.1f  SiO2=%.1f  SG=%.2f"
          % (u, len(s), s.NI_PCT.mean(), s.CO_PCT.mean(), s.FE_PCT.mean(),
             s.MGO_PCT.mean(), s.SIO2_PCT.mean(), s.SG.mean()))
print()
print("korelasi Fe vs MgO :", round(asy.FE_PCT.corr(asy.MGO_PCT), 3))
print("korelasi Ni vs MgO :", round(asy.NI_PCT.corr(asy.MGO_PCT), 3))
sap = m[m.LITH == "SAP"]
print("saprolit Ni: mean %.2f median %.2f max %.2f CV %.2f"
      % (sap.NI_PCT.mean(), sap.NI_PCT.median(), sap.NI_PCT.max(),
         sap.NI_PCT.std() / sap.NI_PCT.mean()))
print("tebal saprolit rata2:", round(lit[lit.LITH == "SAP"].eval("TO-FROM").mean(), 1), "m")
print("tebal limonit rata2 :", round(lit[lit.LITH == "LIM"].eval("TO-FROM").mean(), 1), "m")

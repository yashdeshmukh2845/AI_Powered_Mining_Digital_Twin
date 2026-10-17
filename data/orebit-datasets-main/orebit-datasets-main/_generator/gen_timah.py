"""
gen_timah.py - dataset sintetis TIMAH ALUVIAL (placer).
Analog gaya endapan: placer kasiterit Bangka-Belitung, pemboran "bor Banka".
Blok FIKTIF "Sungai Berumput". Semua angka dihasilkan model, bukan data nyata.

Karakter yang sengaja dibangun:
  - bor vertikal dangkal pada grid lintasan: lintasan 100 m, titik 25 m
  - permukaan bedrock (kong, granit terkaolinisasi) berupa paleochannel
    yang berkelok; kedalaman 5 m di interfluve, sampai ~20 m di thalweg
  - kasiterit terkonsentrasi pada lapisan kaksa tepat di atas bedrock,
    makin kaya ke arah dasar dan ke arah sumbu channel
  - kadar dilaporkan kg/m3 (konvensi placer timah Indonesia), sangat erratic
  - sebagian lubang "buntu": berhenti sebelum menyentuh bedrock
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SmoothNoise

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "03-timah-placer")
SEED = 20260831
rng = np.random.default_rng(SEED)

X0, Y0 = 612000.0, 9757000.0          # UTM 48S, Bangka (fiktif)
EX, EY = 700.0, 2000.0

topo_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 620, 2, 2)
mnd_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 480, 2, 2)
base_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 260, 3, 2)
top_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 210, 2, 2)
kak_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 190, 2, 2)
pay_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 150, 3, 2)
fac_n = SmoothNoise(rng, (0, 0), (EX + 200, EY + 200), 120, 2, 2)
g3 = SmoothNoise(rng, (0, 0, -200), (EX + 200, EY + 200, 400), 60, 2, 3)

W_CH = 115.0        # setengah lebar channel (m)
W_SN = 88.0         # setengah lebar pay streak (m)
A_INC = 12.5        # kedalaman insisi maksimum channel (m)


def topo(x, y):
    """Dataran aluvial rendah, elevasi ~7-27 m."""
    return 16.0 + 5.2 * topo_n(x, y) + 0.0022 * y


def thalweg_x(y):
    """Posisi sumbu paleochannel (meander) pada koordinat X."""
    y = np.asarray(y, dtype=float)
    return (330.0 + 88.0 * np.sin(y / 360.0)
            + 46.0 * mnd_n(np.full_like(y, 350.0), y))


def bedrock_depth(x, y):
    """Kedalaman ke permukaan bedrock/kong (m di bawah permukaan tanah)."""
    dx = x - thalweg_x(y)
    inc = A_INC * np.exp(-0.5 * (dx / W_CH) ** 2)
    base = 5.0 + 1.7 * base_n(x, y)
    return np.clip(base + inc, 2.2, 24.0)


rows_col, rows_sur, rows_asy, rows_lit = [], [], [], []
lines = np.arange(50.0, EY, 100.0)          # lintasan arah timur-barat
stations = np.arange(50.0, 651.0, 25.0)     # titik bor sepanjang lintasan
hid = 0

for li, gy in enumerate(lines, start=1):
    for gx in stations:
        hid += 1
        bhid = "SBR-%02d-%03d" % (li, int(gx))
        x = gx + rng.normal(0, 1.2)
        y = gy + rng.normal(0, 1.2)
        xa, ya = np.array([x]), np.array([y])
        z = float(topo(xa, ya)[0])
        d_brk = float(bedrock_depth(xa, ya)[0])

        t_top = float(np.clip(2.1 + 0.85 * top_n(xa, ya)[0], 0.8, 4.5))
        dx = float(x - thalweg_x(ya)[0])
        # kaksa paling tebal di sumbu channel
        t_kak = float(np.clip((0.55 + 1.9 * np.exp(-0.5 * (dx / W_CH) ** 2))
                              * (1.0 + 0.32 * kak_n(xa, ya)[0]), 0.0, 4.2))
        t_top = min(t_top, max(d_brk - t_kak - 0.6, 0.5))
        b_top = t_top
        b_alv = max(d_brk - t_kak, b_top + 0.3)
        t_kak = max(d_brk - b_alv, 0.0)

        into_kong = rng.uniform(1.0, 1.8)
        TD = d_brk + into_kong

        # ~4% lubang buntu: berhenti sebelum bedrock (bongkah / runtuh)
        buntu = rng.random() < 0.04
        if buntu:
            TD = b_alv * rng.uniform(0.55, 0.95)
        TD = float(np.round(TD, 1))

        rows_col.append((bhid, X0 + x, Y0 + y, z, TD))
        rows_sur.append((bhid, 0.0, 0.0, 90.0))
        rows_sur.append((bhid, TD, 0.0, 90.0))

        edges = np.arange(0.0, TD + 1e-6, 1.0)
        if edges[-1] < TD - 1e-6:
            edges = np.append(edges, TD)
        if edges.size > 2 and edges[-1] - edges[-2] < 0.3:
            edges = np.delete(edges, -2)      # gabung sisa pendek
        f, t = edges[:-1], edges[1:]
        mid = (f + t) / 2.0

        unit = np.where(mid < b_top, "TOP",
                        np.where(mid < b_alv, "ALV",
                                 np.where(mid < d_brk, "KAK", "KONG")))
        # fasies aluvium: pasir vs lempung
        fac = fac_n(np.full(mid.size, x), np.full(mid.size, y))
        unit = np.where(unit == "ALV", np.where(fac > 0.15, "PSR", "LMP"), unit)

        # --- kadar Sn (kg/m3)
        xs = np.full(mid.size, x)
        ys = np.full(mid.size, y)
        n3 = g3(xs, ys, (z - mid) * 8.0)
        pay = float(pay_n(xa, ya)[0])                 # pay streak sepanjang channel
        lat = np.exp(-0.5 * (dx / W_SN) ** 2)         # dekat sumbu = kaya
        # dalam kaksa: makin ke dasar makin kaya
        rel_k = np.clip((mid - b_alv) / max(t_kak, 1e-6), 0.0, 1.0)
        enrich = 0.55 + 1.35 * rel_k

        log_sn = (np.log10(0.62 * max(lat, 1e-6)) + 0.24 * pay
                  + np.log10(np.clip(enrich, 0.05, None))
                  + 0.30 * (0.7 * n3 + 0.71 * rng.standard_normal(mid.size)))
        sn_kak = 10.0 ** log_sn

        sn = np.where(np.isin(unit, ["KAK"]), sn_kak, 0.0)
        # sedikit kasiterit tercecer di aluvium bawah dan puncak kong lapuk
        sn = np.where(np.isin(unit, ["PSR", "LMP"]),
                      sn_kak * 0.10 * np.exp(-(b_alv - mid) / 2.6), sn)
        sn = np.where(unit == "KONG",
                      sn_kak * 0.16 * np.exp(-(mid - d_brk) / 0.9), sn)
        sn = np.where(unit == "TOP", 10.0 ** (-2.5 + 0.3 * rng.standard_normal(mid.size)), sn)
        sn = np.clip(sn, 0.0, 12.0)
        sn = np.where(sn < 0.005, 0.002, sn)          # setengah limit deteksi

        # densitas curah in-situ
        bd = np.select(
            [unit == "TOP", np.isin(unit, ["PSR", "LMP"]), unit == "KAK"],
            [1.55 + 0.07 * rng.standard_normal(mid.size),
             1.72 + 0.08 * rng.standard_normal(mid.size),
             1.94 + 0.09 * rng.standard_normal(mid.size)],
            default=2.05 + 0.10 * rng.standard_normal(mid.size))

        for j in range(mid.size):
            rows_asy.append((bhid, f[j], t[j], round(float(sn[j]), 4),
                             round(float(bd[j]), 2)))

        b = 0
        for j in range(1, mid.size + 1):
            end = j == mid.size
            if end or unit[j] != unit[b]:
                rows_lit.append((bhid, float(f[b]), float(t[j - 1]), str(unit[b])))
                b = j

col = pd.DataFrame(rows_col, columns=["BHID", "XCOLLAR", "YCOLLAR", "ZCOLLAR", "TD"])
sur = pd.DataFrame(rows_sur, columns=["BHID", "AT", "AZ", "DIP"])
asy = pd.DataFrame(rows_asy, columns=["BHID", "FROM", "TO", "SN_KGM3", "BD_TM3"])
lit = pd.DataFrame(rows_lit, columns=["BHID", "FROM", "TO", "LITH"])

for c, nd in dict(XCOLLAR=2, YCOLLAR=2, ZCOLLAR=2, TD=1).items():
    col[c] = col[c].round(nd)
for c, nd in dict(AT=1, AZ=1, DIP=1).items():
    sur[c] = sur[c].round(nd)
for c in ("FROM", "TO"):
    asy[c] = asy[c].round(2)
    lit[c] = lit[c].round(2)

os.makedirs(OUT, exist_ok=True)
col.to_csv(os.path.join(OUT, "collar.csv"), index=False)
sur.to_csv(os.path.join(OUT, "survey.csv"), index=False)
asy.to_csv(os.path.join(OUT, "assay.csv"), index=False)
lit.to_csv(os.path.join(OUT, "litho.csv"), index=False)

m = asy.merge(lit, on="BHID")
m = m[(m.FROM_x >= m.FROM_y) & (m.TO_x <= m.TO_y)]
k = m[m.LITH == "KAK"]
print("lubang    :", len(col), "| meter bor:", round(col.TD.sum()))
print("assay     :", len(asy), "| litologi:", len(lit))
print("TD min/med/max:", col.TD.min(), col.TD.median(), col.TD.max())
print()
for u in ["TOP", "PSR", "LMP", "KAK", "KONG"]:
    s = m[m.LITH == u]
    if len(s):
        print("%-5s n=%5d  Sn mean %.3f  median %.3f  max %.2f  kg/m3"
              % (u, len(s), s.SN_KGM3.mean(), s.SN_KGM3.median(), s.SN_KGM3.max()))
print()
print("KAKSA: CV %.2f | tebal rata2 %.2f m"
      % (k.SN_KGM3.std() / k.SN_KGM3.mean(),
         lit[lit.LITH == "KAK"].eval("TO-FROM").mean()))
print("proporsi kaksa >0.2 kg/m3 :", round((k.SN_KGM3 > 0.2).mean() * 100, 1), "%")
print("lubang buntu (tanpa KONG) :", col.BHID.nunique() - lit[lit.LITH == "KONG"].BHID.nunique())

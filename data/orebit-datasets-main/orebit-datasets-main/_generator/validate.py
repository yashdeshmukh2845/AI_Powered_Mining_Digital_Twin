"""
validate.py - pemeriksaan integritas dan kewajaran geologi ketiga dataset.
Dijalankan setelah generator. Keluaran dipakai untuk mengisi README.
"""
import os
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SETS = [("01-emas-epitermal", "AU_GPT", "g/t"),
        ("02-nikel-laterit", "NI_PCT", "%"),
        ("03-timah-placer", "SN_KGM3", "kg/m3")]

fail = 0


def chk(cond, msg):
    global fail
    print(("   OK   " if cond else "  GAGAL ") + msg)
    if not cond:
        fail += 1


def nn_spacing(col):
    P = col[["XCOLLAR", "YCOLLAR"]].to_numpy()
    d = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    return np.median(d.min(1))


for folder, gcol, unit in SETS:
    d = os.path.join(BASE, folder)
    col = pd.read_csv(os.path.join(d, "collar.csv"))
    sur = pd.read_csv(os.path.join(d, "survey.csv"))
    asy = pd.read_csv(os.path.join(d, "assay.csv"))
    lit = pd.read_csv(os.path.join(d, "litho.csv"))

    print("\n" + "=" * 68)
    print(folder)
    print("=" * 68)
    print("collar %d | survey %d | assay %d | litho %d"
          % (len(col), len(sur), len(asy), len(lit)))

    # --- integritas referensial
    chk(col.BHID.is_unique, "BHID collar unik (tidak ada duplikat)")
    chk(set(asy.BHID) <= set(col.BHID), "semua BHID assay ada di collar")
    chk(set(sur.BHID) <= set(col.BHID), "semua BHID survey ada di collar")
    chk(set(lit.BHID) <= set(col.BHID), "semua BHID litho ada di collar")
    chk(set(col.BHID) == set(sur.BHID), "setiap lubang punya survey")

    # --- geometri interval
    chk((asy.TO > asy.FROM).all(), "assay FROM < TO di semua baris")
    chk((lit.TO > lit.FROM).all(), "litho FROM < TO di semua baris")
    chk((asy.FROM >= -1e-9).all(), "tidak ada assay FROM negatif")

    ov = 0
    gp = 0
    for b, g in asy.sort_values(["BHID", "FROM"]).groupby("BHID"):
        f = g.FROM.to_numpy()
        t = g.TO.to_numpy()
        ov += int((f[1:] < t[:-1] - 1e-6).sum())
        gp += int((f[1:] > t[:-1] + 1e-6).sum())
    chk(ov == 0, "tidak ada interval assay bertumpang tindih (overlap=%d)" % ov)
    print("        celah antar interval assay: %d (wajar bila ada casing/tak diassay)" % gp)

    mx = asy.groupby("BHID").TO.max()
    td = col.set_index("BHID").TD
    over = (mx - td.reindex(mx.index)).max()
    chk(over <= 0.051, "assay tidak melewati TD collar (maks lebih %.2f m)" % over)
    smx = sur.groupby("BHID").AT.max()
    chk((smx - td.reindex(smx.index)).max() <= 0.051, "survey AT tidak melewati TD")

    chk(sur.AZ.between(0, 360).all(), "azimut survey 0-360")
    chk(sur.DIP.between(0, 90).all(), "dip survey 0-90 (konvensi positif ke bawah)")

    # --- kewajaran kadar
    g = asy[gcol].dropna()
    chk((g >= 0).all(), "tidak ada kadar negatif")
    print("        %s: n=%d mean=%.4f median=%.4f max=%.3f CV=%.2f  [%s]"
          % (gcol, len(g), g.mean(), g.median(), g.max(),
             g.std() / g.mean(), unit))
    q = g.quantile([0.5, 0.9, 0.99, 0.999]).round(4).to_dict()
    print("        kuantil P50/P90/P99/P99.9:", q)

    print("        spasi collar tetangga terdekat (median): %.1f m" % nn_spacing(col))
    print("        TD  min/median/max: %.1f / %.1f / %.1f m"
          % (col.TD.min(), col.TD.median(), col.TD.max()))
    print("        sebaran X %.0f m, Y %.0f m, Z %.0f m"
          % (col.XCOLLAR.max() - col.XCOLLAR.min(),
             col.YCOLLAR.max() - col.YCOLLAR.min(),
             col.ZCOLLAR.max() - col.ZCOLLAR.min()))
    print("        panjang sampel: modus %.2f m, min %.2f, maks %.2f"
          % ((asy.TO - asy.FROM).mode()[0], (asy.TO - asy.FROM).min(),
             (asy.TO - asy.FROM).max()))
    print("        litologi:", lit.LITH.value_counts().to_dict())
    nulls = {c: int(asy[c].isna().sum()) for c in asy.columns
             if asy[c].isna().any()}
    print("        nilai kosong:", nulls if nulls else "tidak ada")

print("\n" + "=" * 68)
print("PEMERIKSAAN GAGAL:", fail)
print("=" * 68)

# A failed validation must also fail the shell/CI job.
raise SystemExit(1 if fail else 0)

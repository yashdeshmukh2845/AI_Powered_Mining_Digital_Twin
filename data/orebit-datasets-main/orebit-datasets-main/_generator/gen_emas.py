"""
gen_emas.py - dataset sintetis EMAS, urat epitermal low-sulphidation.
Analog gaya endapan: Pongkor / Cikotok, Jawa Barat (busur Sunda-Banda).
Prospek FIKTIF "Cikaruncang". Semua angka dihasilkan model, bukan data nyata.

Karakter yang sengaja dibangun:
  - urat tabular curam (dip 75 deg ke 070), tebal 1-16 m, pinch & swell
  - ore shoot menunjam ~45 deg di dalam bidang urat
  - Au sangat erratic: CV ~2, nugget tinggi, range pendek (~25 m)
  - Ag berkorelasi dengan Au, rasio Ag:Au ~10-15 (khas LS epitermal)
  - bor berarah memotong urat, sampel 1 m di zona urat, 2 m di waste
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SmoothNoise, desurvey, hole_vector, D2R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "01-emas-epitermal")
SEED = 20260829
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- geometri
X0, Y0, Z0 = 682500.0, 9243000.0, 892.0     # acuan bidang urat, dekat subcrop
STRIKE, DIP = 340.0, 75.0                    # dip ke 070 (ENE)

s_hat = np.array([np.sin(STRIKE * D2R), np.cos(STRIKE * D2R), 0.0])
dipdir = (STRIKE + 90.0) * D2R
d_hat = np.array([np.sin(dipdir) * np.cos(DIP * D2R),
                  np.cos(dipdir) * np.cos(DIP * D2R),
                  -np.sin(DIP * D2R)])
d_hat /= np.linalg.norm(d_hat)
n_hat = np.cross(s_hat, d_hat)
n_hat /= np.linalg.norm(n_hat)
P0 = np.array([X0, Y0, Z0])

U_MIN, U_MAX = -450.0, 450.0     # panjang jurus 900 m
V_MIN, V_MAX = -40.0, 340.0      # penunjaman 380 m


def uvw(P):
    """XYZ -> koordinat lokal urat (u=jurus, v=down-dip, w=tegak lurus urat)."""
    q = P - P0
    return q @ s_hat, q @ d_hat, q @ n_hat


# ------------------------------------------------------------------ medan
topo_n = SmoothNoise(rng, (X0 - 900, Y0 - 900), (1800, 1800), 420, 3, 2)
thick_n = SmoothNoise(rng, (U_MIN, V_MIN), (900, 380), 130, 3, 2)
shoot_n = SmoothNoise(rng, (U_MIN, V_MIN), (900, 380), 260, 2, 2)
au_str = SmoothNoise(rng, (X0 - 900, Y0 - 900, 200), (1800, 1800, 900), 26, 2, 3)
ag_str = SmoothNoise(rng, (X0 - 900, Y0 - 900, 200), (1800, 1800, 900), 40, 2, 3)
lit_n = SmoothNoise(rng, (X0 - 900, Y0 - 900, 200), (1800, 1800, 900), 150, 2, 3)


def topo(x, y):
    """Topografi perbukitan vulkanik, elevasi ~780-980 m."""
    return (880.0 + 52.0 * topo_n(x, y)
            + 0.020 * (y - Y0) - 0.012 * (x - X0))


def vein_thickness(u, v):
    """Tebal urat (m). Pinch & swell; <0.7 m dianggap urat memipih habis."""
    t = 5.2 + 3.1 * thick_n(u, v)
    # menipis ke arah ujung jurus dan ke bawah (tipikal urat epitermal)
    taper = np.clip(1.0 - ((np.abs(u) - 300.0) / 190.0), 0.15, 1.0)
    taper *= np.clip(1.0 - ((v - 210.0) / 175.0), 0.20, 1.0)
    return np.clip(t * taper, 0.0, 16.0)


# tiga ore shoot menunjam ~45 deg (arah +u, +v) di dalam bidang urat
SHOOTS = [(-250.0, 70.0, 130.0, 55.0, 0.78),
          (30.0, 120.0, 155.0, 60.0, 0.86),
          (255.0, 60.0, 110.0, 48.0, 0.62)]
PLUNGE = 45.0 * D2R


def shoot_boost(u, v):
    """Tambahan log10(Au) dari ore shoot yang menunjam di bidang urat."""
    b = np.zeros_like(np.asarray(u, dtype=float))
    for cu, cv, la, wa, amp in SHOOTS:
        du, dv = u - cu, v - cv
        a = du * np.cos(PLUNGE) + dv * np.sin(PLUNGE)     # sepanjang penunjaman
        c = -du * np.sin(PLUNGE) + dv * np.cos(PLUNGE)    # melintang
        b = b + amp * np.exp(-0.5 * ((a / la) ** 2 + (c / wa) ** 2))
    return b + 0.16 * shoot_n(u, v)


def model(P):
    """Evaluasi model di titik XYZ. Kembalikan dict array."""
    u, v, w = uvw(P)
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    t = vein_thickness(u, v)
    half = t / 2.0
    inside_env = (u > U_MIN) & (u < U_MAX) & (v > V_MIN) & (v < V_MAX)

    in_vein = inside_env & (np.abs(w) <= half) & (t >= 0.7)
    halo_w = 3.0 + 2.5 * np.abs(thick_n(u, v))
    in_stk = inside_env & ~in_vein & (np.abs(w) <= half + halo_w) & (t >= 0.5)

    # --- Au: nugget tinggi (45%) + struktur pendek (55%), sigma log10 ~0.55
    zf = 0.74 * au_str(x, y, z) + 0.67 * rng.standard_normal(x.size)
    zf = np.clip(zf, -3.0, 3.2)
    log_au = 0.30 + shoot_boost(u, v) + 0.55 * zf
    au = np.where(in_vein, 10.0 ** log_au, 0.0)

    # halo stockwork: kadar rendah, meluruh menjauhi urat
    dist_out = np.clip(np.abs(w) - half, 0.0, None)
    au_h = 10.0 ** (-0.55 + 0.30 * zf) * np.exp(-dist_out / 3.2)
    au = np.where(in_stk, au_h, au)

    # batuan samping: latar sangat rendah
    au_bg = 10.0 ** (-1.85 + 0.34 * rng.standard_normal(x.size))
    au = np.where(in_vein | in_stk, au, au_bg)

    # --- Ag: rasio Ag:Au ~10-15, sebagian berkorelasi
    log_ratio = (np.log10(11.5) + 0.17 * ag_str(x, y, z)
                 + 0.13 * rng.standard_normal(x.size))
    ag = au * 10.0 ** log_ratio
    ag = np.where(in_vein | in_stk, ag,
                  10.0 ** (-0.80 + 0.34 * rng.standard_normal(x.size)))

    # --- litologi & alterasi
    lith = np.where(lit_n(x, y, z) > 0.45, "TUF", "AND").astype(object)
    lith = np.where(in_stk, "STK", lith)
    lith = np.where(in_vein, "VN", lith)
    # breksi hidrotermal di tepi urat pada zona tebal
    lith = np.where(in_vein & (t > 8.5) & (np.abs(w) > half * 0.72), "BX", lith)

    dtot = np.where(in_vein, 0.0, dist_out)
    alt = np.full(x.size, "PROP", dtype=object)
    alt = np.where(dtot < 22.0, "ARG", alt)
    alt = np.where(dtot < 7.0, "ADL", alt)
    alt = np.where(in_vein, "SIL", alt)
    alt = np.where((~inside_env) & (dtot > 45.0), "FRESH", alt)

    # --- densitas curah
    sg = np.select(
        [in_vein, in_stk],
        [2.62 + 0.05 * rng.standard_normal(x.size),
         2.57 + 0.05 * rng.standard_normal(x.size)],
        default=2.52 + 0.06 * rng.standard_normal(x.size))

    return dict(u=u, v=v, w=w, au=au, ag=ag, lith=lith, alt=alt, sg=sg,
                in_vein=in_vein, in_stk=in_stk)


# --------------------------------------------------------------- pemboran
def collar_for_target(u_t, v_t, az, dip):
    """Hitung posisi collar agar lubang mendarat di titik (u_t, v_t) pada urat."""
    T = P0 + u_t * s_hat + v_t * d_hat
    h = hole_vector(az, dip)
    L = max((topo(T[0], T[1]) - T[2]) / np.sin(dip * D2R), 20.0)
    for _ in range(8):
        C = T - L * h
        zt = float(topo(np.array([C[0]]), np.array([C[1]]))[0])
        L = np.clip(L + (zt - C[2]) / np.sin(dip * D2R), 20.0, 700.0)
    C = T - L * h
    C[2] = float(topo(np.array([C[0]]), np.array([C[1]]))[0])
    return C, L


rows_col, rows_sur, rows_asy, rows_lit = [], [], [], []
sections = np.arange(-420.0, 421.0, 30.0)
targets_v = [30.0, 100.0, 180.0, 265.0]
hid = 0

for u_s in sections:
    for k, v_t in enumerate(targets_v):
        # lubang lebih dalam makin jarang di sayap (pola pemboran bertahap)
        if abs(u_s) > 330 and k >= 2:
            continue
        if abs(u_s) > 240 and k == 3 and rng.random() < 0.55:
            continue
        hid += 1
        bhid = "CKR-%03d" % hid
        u_t = u_s + rng.normal(0, 4.0)
        v_tt = v_t + rng.normal(0, 12.0)
        az0 = 250.0 + rng.normal(0, 4.0)
        dip0 = np.clip(58.0 + rng.normal(0, 3.5), 48.0, 68.0)
        C, L = collar_for_target(u_t, v_tt, az0, dip0)
        TD = float(np.round(L + rng.uniform(22.0, 46.0), 1))

        # --- survey: drift azimut acak + dip melandai perlahan
        at = np.arange(0.0, TD + 1e-6, 30.0)
        if at[-1] < TD - 1e-6:
            at = np.append(at, TD)
        az_walk = np.cumsum(rng.normal(0, 1.4, at.size)) * np.sqrt(at / 30.0 + 1)
        azs = az0 + az_walk - az_walk[0]
        dips = dip0 - 0.55 * (at / 30.0) + np.cumsum(rng.normal(0, 0.35, at.size))
        dips = np.clip(dips, 35.0, 89.0)
        for a, z_, d_ in zip(at, azs % 360.0, dips):
            rows_sur.append((bhid, a, z_, d_))

        # --- jejak lubang
        step = np.arange(0.0, TD + 1e-6, 0.5)
        off = desurvey(at, azs, dips, step)
        P = C[None, :] + off
        m = model(P)

        # zona sampling rapat = urat + halo + 6 m penyangga
        near = m["in_vein"] | m["in_stk"]
        near_d = step[near]
        lo = near_d.min() - 6.0 if near_d.size else -1
        hi = near_d.max() + 6.0 if near_d.size else -1

        # --- bangun interval sampel
        casing = float(np.round(rng.uniform(2.0, 6.0), 1))
        ivs, cur = [], casing
        while cur < TD - 0.05:
            ln = 1.0 if (near_d.size and lo <= cur <= hi) else 2.0
            nxt = min(cur + ln, TD)
            if nxt - cur < 0.3 and ivs:
                ivs[-1] = (ivs[-1][0], nxt)      # gabung sisa pendek
            else:
                ivs.append((cur, nxt))
            cur = nxt

        idx = {round(d, 2): i for i, d in enumerate(step)}
        for f, t_ in ivs:
            mids = np.array([f + (t_ - f) * q for q in (0.25, 0.5, 0.75)])
            ii = [idx.get(round(np.round(mm * 2) / 2, 2), 0) for mm in mids]
            au = float(np.mean(m["au"][ii]))
            ag = float(np.mean(m["ag"][ii]))
            sg = float(np.mean(m["sg"][ii]))
            au = 0.005 if au < 0.01 else au          # setengah limit deteksi
            ag = 0.25 if ag < 0.5 else ag
            rows_asy.append((bhid, f, t_, au, ag, sg))

        # --- log litologi (gabung run yang sama), dari 0 sampai TD
        codes = m["lith"]
        alts = m["alt"]
        b = 0
        for i in range(1, step.size + 1):
            end = i == step.size
            if end or codes[i] != codes[b] or alts[i] != alts[b]:
                f = float(step[b])
                t_ = float(step[i - 1] + 0.5) if not end else TD
                if t_ - f >= 0.5:
                    rows_lit.append((bhid, f, min(t_, TD), codes[b], alts[b]))
                b = i
        rows_col.append((bhid, C[0], C[1], C[2], TD))

# ------------------------------------------------------------------ tulis
col = pd.DataFrame(rows_col, columns=["BHID", "XCOLLAR", "YCOLLAR", "ZCOLLAR", "TD"])
sur = pd.DataFrame(rows_sur, columns=["BHID", "AT", "AZ", "DIP"])
asy = pd.DataFrame(rows_asy, columns=["BHID", "FROM", "TO", "AU_GPT", "AG_GPT", "SG"])
lit = pd.DataFrame(rows_lit, columns=["BHID", "FROM", "TO", "LITH", "ALT"])

# tanah penutup di puncak lubang -> tidak diassay (nilai kosong), realistis
top = asy.groupby("BHID")["FROM"].transform("min")
asy.loc[asy["FROM"] <= top + 0.01, ["AU_GPT", "AG_GPT"]] = np.nan

for c, nd in dict(XCOLLAR=2, YCOLLAR=2, ZCOLLAR=2, TD=1).items():
    col[c] = col[c].round(nd)
for c, nd in dict(AT=1, AZ=1, DIP=1).items():
    sur[c] = sur[c].round(nd)
for c, nd in dict(FROM=2, TO=2, AU_GPT=3, AG_GPT=2, SG=2).items():
    asy[c] = asy[c].round(nd)
for c in ("FROM", "TO"):
    lit[c] = lit[c].round(2)

os.makedirs(OUT, exist_ok=True)
col.to_csv(os.path.join(OUT, "collar.csv"), index=False)
sur.to_csv(os.path.join(OUT, "survey.csv"), index=False)
asy.to_csv(os.path.join(OUT, "assay.csv"), index=False)
lit.to_csv(os.path.join(OUT, "litho.csv"), index=False)

inv = asy.merge(lit[lit.LITH.isin(["VN", "BX"])], on="BHID", suffixes=("", "_l"))
inv = inv[(inv.FROM >= inv.FROM_l) & (inv.TO <= inv.TO_l)]
print("lubang        :", len(col))
print("meter bor     :", round(col.TD.sum()))
print("survey        :", len(sur))
print("assay         :", len(asy), "| kosong:", int(asy.AU_GPT.isna().sum()))
print("litologi      :", len(lit))
print("--- Au dalam urat (VN/BX) ---")
print("n            :", len(inv))
print("mean  g/t    :", round(inv.AU_GPT.mean(), 2))
print("median g/t   :", round(inv.AU_GPT.median(), 2))
print("max   g/t    :", round(inv.AU_GPT.max(), 1))
print("CV           :", round(inv.AU_GPT.std() / inv.AU_GPT.mean(), 2))
print("Ag/Au median :", round((inv.AG_GPT / inv.AU_GPT).median(), 1))
print("--- semua sampel ---")
print("Au mean      :", round(asy.AU_GPT.mean(), 3))
print("lith counts  :", lit.LITH.value_counts().to_dict())

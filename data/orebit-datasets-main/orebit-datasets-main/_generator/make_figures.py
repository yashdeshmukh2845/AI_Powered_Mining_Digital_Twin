"""
make_figures.py - gambar pendukung untuk rilis dataset (LinkedIn / README).
Semua digambar langsung dari file CSV yang dirilis, bukan dari model.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import desurvey, D2R

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(B, "figures")
os.makedirs(OUT, exist_ok=True)

NAVY = "#1E3037"
NAVY_D = "#161d21"
PAPER = "#F4F6F4"
TEAL = "#0D9488"
BLUE = "#1770B9"
MUTED = "#8fa3ab"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": NAVY_D,
    "axes.facecolor": NAVY,
    "savefig.facecolor": NAVY_D,
    "text.color": PAPER,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": "#3a4a52",
})


def midpoints(d):
    """Kembalikan assay + koordinat XYZ titik tengah tiap interval."""
    col = pd.read_csv(os.path.join(B, d, "collar.csv")).set_index("BHID")
    sur = pd.read_csv(os.path.join(B, d, "survey.csv"))
    asy = pd.read_csv(os.path.join(B, d, "assay.csv"))
    out = []
    for bh, g in asy.groupby("BHID"):
        s = sur[sur.BHID == bh].sort_values("AT")
        mid = ((g.FROM + g.TO) / 2.0).to_numpy()
        off = desurvey(s.AT.to_numpy(), s.AZ.to_numpy(), s.DIP.to_numpy(), mid)
        c = col.loc[bh]
        q = g.copy()
        q["X"] = c.XCOLLAR + off[:, 0]
        q["Y"] = c.YCOLLAR + off[:, 1]
        q["Z"] = c.ZCOLLAR + off[:, 2]
        out.append(q)
    return pd.concat(out, ignore_index=True)


# ==========================================================================
# GAMBAR 1 - tiga gaya endapan, tiga masalah estimasi
# ==========================================================================
fig = plt.figure(figsize=(12, 13.5), dpi=100)
gs = fig.add_gridspec(3, 1, hspace=0.40, left=0.085, right=0.90,
                      top=0.878, bottom=0.055)

fig.text(0.085, 0.958, "Three commodities. Three different problems.",
         fontsize=25, fontweight="bold", color=PAPER)
fig.text(0.085, 0.928,
         "Orebit synthetic drillhole datasets  ·  open licence, CC BY 4.0  "
         "·  plotted from the released CSVs",
         fontsize=12.5, color=TEAL)

# ---- A. EMAS: penampang memanjang pada bidang urat
ax = fig.add_subplot(gs[0])
g = midpoints("01-emas-epitermal")
lit = pd.read_csv(os.path.join(B, "01-emas-epitermal", "litho.csv"))
vn = lit[lit.LITH.isin(["VN", "BX"])]
key = set(zip(vn.BHID, vn.FROM))
STRIKE, DIP = 340.0, 75.0
P0 = np.array([682500.0, 9243000.0, 892.0])
s_hat = np.array([np.sin(STRIKE * D2R), np.cos(STRIKE * D2R), 0.0])
dd = (STRIKE + 90.0) * D2R
d_hat = np.array([np.sin(dd) * np.cos(DIP * D2R), np.cos(dd) * np.cos(DIP * D2R),
                  -np.sin(DIP * D2R)])
d_hat /= np.linalg.norm(d_hat)
n_hat = np.cross(s_hat, d_hat); n_hat /= np.linalg.norm(n_hat)
P = g[["X", "Y", "Z"]].to_numpy() - P0
g["u"], g["v"], g["w"] = P @ s_hat, P @ d_hat, P @ n_hat
sel = g[(np.abs(g.w) < 9.0) & g.AU_GPT.notna() & (g.AU_GPT > 0.005)]
sc = ax.scatter(sel.u, -sel.v, c=sel.AU_GPT, s=26, cmap="inferno",
                norm=LogNorm(vmin=0.05, vmax=60), linewidths=0)
cb = fig.colorbar(sc, ax=ax, pad=0.012, fraction=0.028)
cb.set_label("Au  g/t", color=MUTED, fontsize=10)
cb.ax.tick_params(colors=MUTED, labelsize=9)
cb.outline.set_edgecolor("#3a4a52")
ax.set_title("Epithermal gold  ·  long section on the vein plane  ·  "
             "103 holes, 20,187 m",
             color=PAPER, fontsize=14, fontweight="bold", loc="left", pad=9)
ax.set_xlabel("along strike  (m)", fontsize=10)
ax.set_ylabel("down dip  (m)", fontsize=10)
ax.text(0.985, 0.06, "Au CV 1.66  ·  three ore shoots",
        transform=ax.transAxes, ha="right", fontsize=11.5, color=TEAL,
        fontweight="bold", zorder=12,
        bbox=dict(facecolor=NAVY, edgecolor="#3a4a52", alpha=1.0, pad=5))
ax.grid(alpha=0.11, color=PAPER)

# ---- B. NIKEL: penampang satu lintasan
ax = fig.add_subplot(gs[1])
col = pd.read_csv(os.path.join(B, "02-nikel-laterit", "collar.csv"))
asy = pd.read_csv(os.path.join(B, "02-nikel-laterit", "assay.csv"))
ycnt = col.YCOLLAR.round(-1).value_counts()
yline = float(ycnt.index[0])
hs = col[(col.YCOLLAR - yline).abs() < 15]
x0n = col.XCOLLAR.min()
d = asy[asy.BHID.isin(hs.BHID)].merge(hs, on="BHID")
d["Zm"] = d.ZCOLLAR - (d.FROM + d.TO) / 2.0
d = d.dropna(subset=["NI_PCT"])
sc = ax.scatter(d.XCOLLAR - x0n, d.Zm, c=d.NI_PCT, s=40, marker="s", cmap="inferno",
                norm=Normalize(0.2, 2.6), linewidths=0)
ax.plot(hs.sort_values("XCOLLAR").XCOLLAR - x0n, hs.sort_values("XCOLLAR").ZCOLLAR,
        color=TEAL, lw=1.6, alpha=0.85, label="ground surface")
cb = fig.colorbar(sc, ax=ax, pad=0.012, fraction=0.028)
cb.set_label("Ni  %", color=MUTED, fontsize=10)
cb.ax.tick_params(colors=MUTED, labelsize=9)
cb.outline.set_edgecolor("#3a4a52")
ax.set_title("Nickel laterite  ·  section along one 100 m grid line  ·  "
             "350 holes, 8,195 m",
             color=PAPER, fontsize=14, fontweight="bold", loc="left", pad=9)
ax.set_xlabel("easting  (m, relative)", fontsize=10)
ax.set_ylabel("elevation  (m)", fontsize=10)
ax.text(0.985, 0.06, "Ni CV 0.28  ·  Fe vs MgO  r = -0.88",
        transform=ax.transAxes, ha="right", fontsize=11.5, color=TEAL,
        fontweight="bold", zorder=12,
        bbox=dict(facecolor=NAVY, edgecolor="#3a4a52", alpha=1.0, pad=5))
ax.legend(loc="upper left", fontsize=9, facecolor=NAVY, edgecolor="#3a4a52",
          labelcolor=MUTED)
ax.grid(alpha=0.11, color=PAPER)

# ---- C. TIMAH: tampak atas paleochannel
ax = fig.add_subplot(gs[2])
col = pd.read_csv(os.path.join(B, "03-timah-placer", "collar.csv"))
lit = pd.read_csv(os.path.join(B, "03-timah-placer", "litho.csv"))
asy = pd.read_csv(os.path.join(B, "03-timah-placer", "assay.csv"))
brk = lit[lit.LITH == "KONG"].groupby("BHID").FROM.min().rename("DBRK")
kak = lit[lit.LITH == "KAK"]
mm = asy.merge(kak, on="BHID")
mm = mm[(mm.FROM_x >= mm.FROM_y) & (mm.TO_x <= mm.TO_y)]
acc = (mm.assign(a=(mm.TO_x - mm.FROM_x) * mm.SN_KGM3)
         .groupby("BHID").a.sum().rename("ACC"))
p = col.join(brk, on="BHID").join(acc, on="BHID")
p["ACC"] = p.ACC.fillna(0.0)
miss = p[p.DBRK.isna()]
p2 = p.dropna(subset=["DBRK"])
x0t, y0t = p.XCOLLAR.min(), p.YCOLLAR.min()
sc = ax.scatter(p2.YCOLLAR - y0t, p2.XCOLLAR - x0t, c=p2.DBRK,
                s=14 + 34 * np.sqrt(p2.ACC), cmap="inferno",
                norm=Normalize(3, 21), linewidths=0.3, edgecolors="#0e1417")
ax.scatter(miss.YCOLLAR - y0t, miss.XCOLLAR - x0t, s=30, marker="x",
           color=TEAL, lw=1.5, label="blocked hole, bedrock not reached")
cb = fig.colorbar(sc, ax=ax, pad=0.012, fraction=0.028)
cb.set_label("depth to bedrock  (m)", color=MUTED, fontsize=10)
cb.ax.tick_params(colors=MUTED, labelsize=9)
cb.outline.set_edgecolor("#3a4a52")
ax.set_title("Alluvial tin  ·  plan view, symbol size = Sn accumulation  ·  "
             "500 holes, 5,867 m",
             color=PAPER, fontsize=14, fontweight="bold", loc="left", pad=9)
ax.set_xlabel("northing  (m, relative)", fontsize=10)
ax.set_ylabel("easting  (m, rel.)", fontsize=10)
ax.set_aspect("equal")
ax.text(0.985, 0.055, "Sn CV 1.42  ·  ore in the palaeochannel",
        transform=ax.transAxes, ha="right", fontsize=11.5, color=TEAL,
        fontweight="bold", zorder=12,
        bbox=dict(facecolor=NAVY, edgecolor="#3a4a52", alpha=1.0, pad=5))
ax.legend(loc="upper left", fontsize=9, facecolor=NAVY, edgecolor="#3a4a52",
          labelcolor=MUTED)
ax.grid(alpha=0.11, color=PAPER)

fig.text(0.085, 0.018, "orebit.id  ·  geosuite.orebit.id", fontsize=11,
         color=MUTED)
fig.savefig(os.path.join(OUT, "deposit-styles.png"))
plt.close(fig)
print("GAMBAR-1 selesai")


# ==========================================================================
# GAMBAR 2 - sebaran kadar: satu alur kerja, tiga masalah statistik
# ==========================================================================
SETS = [
    ("01-emas-epitermal", "AU_GPT", "Au  (g/t)", "Epithermal gold",
     "in vein (VN + BX)", ["VN", "BX"], True, "#F2A03D"),
    ("02-nikel-laterit", "NI_PCT", "Ni  (%)", "Nickel laterite",
     "in saprolite (SAP)", ["SAP"], False, TEAL),
    ("03-timah-placer", "SN_KGM3", "Sn  (kg/m3)", "Alluvial tin",
     "in kaksa (KAK)", ["KAK"], True, BLUE),
]

fig = plt.figure(figsize=(12, 13.5), dpi=100)
gs = fig.add_gridspec(3, 1, hspace=0.44, left=0.10, right=0.955,
                      top=0.872, bottom=0.082)
fig.text(0.10, 0.953, "Same format. Nothing else in common.",
         fontsize=25, fontweight="bold", color=PAPER)
fig.text(0.10, 0.922,
         "Grade distribution inside the mineralised domain of each dataset. "
         "Note the x axis: two are logarithmic.",
         fontsize=12.5, color=TEAL)

for i, (d, gc, xlab, name, dom, codes, logx, colr) in enumerate(SETS):
    ax = fig.add_subplot(gs[i])
    a = pd.read_csv(os.path.join(B, d, "assay.csv"))
    l = pd.read_csv(os.path.join(B, d, "litho.csv"))
    m = a.merge(l, on="BHID")
    m = m[(m.FROM_x >= m.FROM_y) & (m.TO_x <= m.TO_y)]
    v = m[m.LITH.isin(codes)][gc].dropna()
    v = v[v > 0]
    if logx:
        bins = np.logspace(np.log10(max(v.min(), 1e-3)), np.log10(v.max()), 46)
        ax.set_xscale("log")
    else:
        bins = np.linspace(v.min(), v.max(), 46)
    ax.hist(v, bins=bins, color=colr, alpha=0.92, edgecolor=NAVY_D, linewidth=0.6)
    cv = v.std() / v.mean()
    ax.axvline(v.mean(), color=PAPER, lw=1.7, ls="-", label="mean %.3g" % v.mean())
    ax.axvline(v.median(), color=PAPER, lw=1.7, ls=":", label="median %.3g" % v.median())
    ax.set_title("%s  -  %s  -  n = %s assayed" % (name, dom, format(len(v), ",")),
                 color=PAPER, fontsize=14, fontweight="bold", loc="left", pad=9)
    ax.set_xlabel(xlab, fontsize=10)
    ax.set_ylabel("samples", fontsize=10)
    ax.legend(loc="upper right", fontsize=9.5, facecolor=NAVY,
              edgecolor="#3a4a52", labelcolor=PAPER)
    ax.text(0.012, 0.88, "CV %.2f" % cv, transform=ax.transAxes, fontsize=27,
            fontweight="bold", color=colr, va="top")
    ax.text(0.012, 0.62, "max %.3g" % v.max(), transform=ax.transAxes,
            fontsize=12, color=MUTED, va="top")
    ax.grid(alpha=0.11, color=PAPER, axis="y")

fig.text(0.10, 0.016,
         "One erratic, one smooth, one thin and skewed  -  "
         "orebit.id  -  CC BY 4.0", fontsize=11, color=MUTED)
fig.savefig(os.path.join(OUT, "grade-distributions.png"))
plt.close(fig)
print("GAMBAR-2 selesai")

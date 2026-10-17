"""
check_readme.py - verifikasi bahwa setiap angka yang dikutip di README
benar-benar cocok dengan isi file CSV. Dijalankan setelah dokumentasi ditulis.
"""
import os
import re
import numpy as np
import pandas as pd

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
bad = 0


def ck(label, got, want, tol=0.006):
    global bad
    ok = abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))
    print(("  OK   " if ok else " GAGAL ") + "%-46s README=%s  data=%s"
          % (label, want, round(float(got), 4)))
    if not ok:
        bad += 1


def load(d):
    p = os.path.join(B, d)
    c = pd.read_csv(os.path.join(p, "collar.csv"))
    s = pd.read_csv(os.path.join(p, "survey.csv"))
    a = pd.read_csv(os.path.join(p, "assay.csv"))
    l = pd.read_csv(os.path.join(p, "litho.csv"))
    m = a.merge(l, on="BHID")
    m = m[(m.FROM_x >= m.FROM_y) & (m.TO_x <= m.TO_y)]
    return c, s, a, l, m


print("=" * 74)
print("EMAS")
c, s, a, l, m = load("01-emas-epitermal")
v = m[m.LITH.isin(["VN", "BX"])]
ck("collar", len(c), 103, 0); ck("survey", len(s), 828, 0)
ck("assay", len(a), 11526, 0); ck("litho", len(l), 994, 0)
ck("meter bor", c.TD.sum(), 20187, 0.001)
ck("lubang memotong urat", l[l.LITH.isin(["VN","BX"])].BHID.nunique(), 99, 0)
ck("lebar downhole median", l[l.LITH.isin(["VN","BX"])].assign(W=lambda d: d.TO-d.FROM).groupby("BHID").W.sum().median(), 7.5, 0.02)
ck("Au dalam urat n", len(v), 652, 0)
ck("Au mean", v.AU_GPT.mean(), 5.94); ck("Au median", v.AU_GPT.median(), 2.63)
ck("Au max", v.AU_GPT.max(), 75.0, 0.01); ck("Au CV", v.AU_GPT.std()/v.AU_GPT.mean(), 1.66)
ck("Ag/Au median", (v.AG_GPT/v.AU_GPT).median(), 12.2)
ck("assay terisi", a.AU_GPT.notna().sum(), 11423, 0)
ck("semua sampel mean", a.AU_GPT.mean(), 0.428, 0.01)
ck("semua sampel median", a.AU_GPT.median(), 0.019, 0.03)
ck("% di bawah limit deteksi", 100*(a.AU_GPT<=0.005).mean(), 11.9, 0.02)
ck("SG min", a.SG.min(), 2.33); ck("SG max", a.SG.max(), 2.76)
ck("Z min", c.ZCOLLAR.min(), 750, 0.002); ck("Z max", c.ZCOLLAR.max(), 1002, 0.002)
ck("TD min", c.TD.min(), 45, 0.02); ck("TD max", c.TD.max(), 409, 0.01)

print("=" * 74)
print("NIKEL")
c, s, a, l, m = load("02-nikel-laterit")
sap, lim = m[m.LITH == "SAP"], m[m.LITH == "LIM"]
ck("collar", len(c), 350, 0); ck("survey", len(s), 700, 0)
ck("assay", len(a), 8278, 0); ck("litho", len(l), 1366, 0)
ck("meter bor", c.TD.sum(), 8195, 0.001)
ck("lubang buntu (tanpa BRK)", len(c)-l[l.LITH=="BRK"].BHID.nunique(), 8, 0)
ck("tebal limonit rata2", l[l.LITH=="LIM"].eval("TO-FROM").mean(), 7.9, 0.02)
ck("tebal saprolit rata2", l[l.LITH=="SAP"].eval("TO-FROM").mean(), 11.7, 0.02)
for e, sv, lv in [("NI_PCT",1.72,1.19),("CO_PCT",0.051,0.119),("FE_PCT",15.1,42.1),
                  ("MGO_PCT",18.1,3.8),("SIO2_PCT",36.2,12.0),("SG",1.65,1.46)]:
    ck("saprolit "+e, sap[e].mean(), sv, 0.02); ck("limonit  "+e, lim[e].mean(), lv, 0.02)
ck("saprolit Al2O3", sap.AL2O3_PCT.mean(), 1.65, 0.02)
ck("limonit  Al2O3", lim.AL2O3_PCT.mean(), 4.93, 0.02)
ck("saprolit Cr2O3", sap.CR2O3_PCT.mean(), 1.17, 0.02)
ck("limonit  Cr2O3", lim.CR2O3_PCT.mean(), 2.25, 0.02)
ck("assay kosong", a.NI_PCT.isna().sum(), 41, 0)
ck("semua Ni mean", a.NI_PCT.mean(), 1.31, 0.01)
ck("semua Ni median", a.NI_PCT.median(), 1.28, 0.01)
ck("semua Ni max", a.NI_PCT.max(), 3.62, 0.01)
ck("semua Ni CV", a.NI_PCT.std()/a.NI_PCT.mean(), 0.47, 0.02)
ck("saprolit n", len(sap), 4085, 0)
ck("saprolit Ni CV", sap.NI_PCT.std()/sap.NI_PCT.mean(), 0.28, 0.02)
ck("saprolit >=1.5% Ni", 100*(sap.NI_PCT>=1.5).mean(), 63.1, 0.01)
ck("SiO2/MgO saprolit", (sap.SIO2_PCT/sap.MGO_PCT).median(), 2.03, 0.01)
ck("korelasi Fe-MgO", a.FE_PCT.corr(a.MGO_PCT), -0.88, 0.01)
ck("Z min", c.ZCOLLAR.min(), 241, 0.003); ck("Z max", c.ZCOLLAR.max(), 396, 0.003)
ck("TD median", c.TD.median(), 23.2, 0.01)

print("=" * 74)
print("TIMAH")
c, s, a, l, m = load("03-timah-placer")
k = m[m.LITH == "KAK"]
gt = k.assign(v=(k.TO_x-k.FROM_x)*k.SN_KGM3).groupby("BHID").v.sum()
ck("collar", len(c), 500, 0); ck("survey", len(s), 1000, 0)
ck("assay", len(a), 5990, 0); ck("litho", len(l), 1853, 0)
ck("meter bor", c.TD.sum(), 5867, 0.001)
ck("lubang buntu", len(c)-l[l.LITH=="KONG"].BHID.nunique(), 26, 0)
ck("lubang dengan kaksa", k.BHID.nunique(), 393, 0)
ck("kaksa n", len(k), 664, 0)
ck("kaksa mean", k.SN_KGM3.mean(), 0.731); ck("kaksa median", k.SN_KGM3.median(), 0.405, 0.01)
ck("kaksa max", k.SN_KGM3.max(), 9.74, 0.01); ck("kaksa CV", k.SN_KGM3.std()/k.SN_KGM3.mean(), 1.42)
ck("kaksa >5 kg/m3 n", (k.SN_KGM3>5).sum(), 8, 0)
ck("kaksa >5 kg/m3 %", 100*(k.SN_KGM3>5).mean(), 1.2, 0.05)
ck("akumulasi median", gt.median(), 0.39, 0.02); ck("akumulasi max", gt.max(), 18.4, 0.01)
ck("semua Sn mean", a.SN_KGM3.mean(), 0.093, 0.02)
ck("tebal kaksa median", l[l.LITH=="KAK"].eval("TO-FROM").median(), 1.0, 0.01)
ck("tebal kaksa max", l[l.LITH=="KAK"].eval("TO-FROM").max(), 4.0, 0.02)
kong = l[l.LITH=="KONG"].groupby("BHID").FROM.min()
ck("kedalaman bedrock max", kong.max(), 21, 0.02)
ck("Z min", c.ZCOLLAR.min(), 8, 0.06); ck("Z max", c.ZCOLLAR.max(), 33, 0.02)
ck("TD min", c.TD.min(), 2.0, 0.02); ck("TD max", c.TD.max(), 22.5, 0.01)
ck("TD median", c.TD.median(), 11.0, 0.01)
ck("sebaran X", c.XCOLLAR.max()-c.XCOLLAR.min(), 604, 0.01)
ck("sebaran Y", c.YCOLLAR.max()-c.YCOLLAR.min(), 1906, 0.01)

print("=" * 74)
print("KLAIM README YANG TIDAK COCOK:", bad)
print("=" * 74)

# A failed validation must also fail the shell/CI job.
raise SystemExit(1 if bad else 0)

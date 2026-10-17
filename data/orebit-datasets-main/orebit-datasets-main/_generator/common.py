"""
common.py - utilitas bersama untuk generator dataset sintetis Orebit.
Hanya butuh numpy + pandas (tanpa scipy).

Berisi:
  SmoothNoise   - medan acak halus (value noise multi-oktaf) untuk memodelkan
                  variasi geologi yang berkorelasi spasial
  desurvey      - desurvey minimum curvature (konvensi DIP positif ke bawah,
                  90 = vertikal ke bawah, sama seperti dataset Babbitt)
"""
import numpy as np

D2R = np.pi / 180.0


# --------------------------------------------------------------------------
# Medan acak halus (value noise). Dipakai untuk ketebalan urat, topografi,
# permukaan bedrock, dan variasi kadar yang berkorelasi spasial.
# --------------------------------------------------------------------------
class SmoothNoise:
    """Value noise multi-oktaf pada 2D atau 3D.

    cell     : ukuran sel oktaf pertama dalam meter (= panjang korelasi kasar)
    octaves  : jumlah oktaf; tiap oktaf setengah ukuran, setengah amplitudo
    """

    def __init__(self, rng, origin, extent, cell, octaves=3, ndim=2):
        self.origin = np.asarray(origin, dtype=float)
        self.ndim = ndim
        self.layers = []
        for o in range(octaves):
            c = cell / (2 ** o)
            shape = tuple(int(e / c) + 4 for e in extent)
            g = rng.normal(0.0, 1.0, shape)
            self.layers.append((c, g, 0.5 ** o))
        # Kalibrasi empiris: interpolasi menurunkan varians, jadi faktor
        # normalisasi diukur langsung dari sampel acak di dalam domain.
        self.norm = 1.0
        probe = [self.origin[k] + rng.uniform(0, extent[k], 20000)
                 for k in range(ndim)]
        self.norm = 1.0 / float(np.std(self(*probe)))

    @staticmethod
    def _smoothstep(t):
        return t * t * (3.0 - 2.0 * t)

    def __call__(self, *coords):
        coords = [np.asarray(c, dtype=float) for c in coords]
        total = np.zeros_like(coords[0], dtype=float)
        for c, g, w in self.layers:
            f = [(coords[k] - self.origin[k]) / c + 1.0 for k in range(self.ndim)]
            i0 = [np.clip(np.floor(f[k]).astype(int), 0, g.shape[k] - 2)
                  for k in range(self.ndim)]
            d = [np.clip(f[k] - i0[k], 0.0, 1.0) for k in range(self.ndim)]
            s = [self._smoothstep(d[k]) for k in range(self.ndim)]
            if self.ndim == 2:
                v00 = g[i0[0], i0[1]]
                v10 = g[i0[0] + 1, i0[1]]
                v01 = g[i0[0], i0[1] + 1]
                v11 = g[i0[0] + 1, i0[1] + 1]
                val = ((v00 * (1 - s[0]) + v10 * s[0]) * (1 - s[1])
                       + (v01 * (1 - s[0]) + v11 * s[0]) * s[1])
            else:
                acc = 0.0
                for a in (0, 1):
                    for b in (0, 1):
                        for cc in (0, 1):
                            wgt = ((s[0] if a else 1 - s[0])
                                   * (s[1] if b else 1 - s[1])
                                   * (s[2] if cc else 1 - s[2]))
                            acc = acc + wgt * g[i0[0] + a, i0[1] + b, i0[2] + cc]
                val = acc
            total = total + w * val
        return total * self.norm


# --------------------------------------------------------------------------
# Desurvey minimum curvature.
# Konvensi: DIP positif ke bawah, 90 = vertikal ke bawah (mengikuti Babbitt).
# Inklinasi dari vertikal I = 90 - DIP.
# Sumbu: X = easting, Y = northing, Z = elevasi (positif ke atas).
# --------------------------------------------------------------------------
def desurvey(at, az, dip, depths):
    """Kembalikan array (n,3) offset XYZ dari collar pada kedalaman `depths`.

    at, az, dip : stasiun survey (kedalaman m, azimut deg, dip deg positif turun)
    depths      : kedalaman yang diminta (m), menaik
    """
    at = np.asarray(at, dtype=float)
    az = np.asarray(az, dtype=float)
    dip = np.asarray(dip, dtype=float)
    depths = np.asarray(depths, dtype=float)

    # Rapatkan menjadi langkah 1 m dengan interpolasi sudut linier,
    # lalu terapkan minimum curvature per langkah.
    dmax = max(depths.max(), at.max())
    fine = np.arange(0.0, dmax + 1.0, 1.0)
    fine = np.unique(np.concatenate([fine, depths, at]))
    fine.sort()

    az_f = np.interp(fine, at, np.unwrap(az * D2R) / D2R)
    dip_f = np.interp(fine, at, dip)

    inc = (90.0 - dip_f) * D2R          # inklinasi dari vertikal
    azr = az_f * D2R

    dmd = np.diff(fine)
    i1, i2 = inc[:-1], inc[1:]
    a1, a2 = azr[:-1], azr[1:]

    cos_beta = (np.cos(i2 - i1)
                - np.sin(i1) * np.sin(i2) * (1.0 - np.cos(a2 - a1)))
    cos_beta = np.clip(cos_beta, -1.0, 1.0)
    beta = np.arccos(cos_beta)
    rf = np.where(beta < 1e-9, 1.0, 2.0 / np.where(beta < 1e-9, 1.0, beta)
                  * np.tan(beta / 2.0))

    de = dmd / 2.0 * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    dn = dmd / 2.0 * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    dv = dmd / 2.0 * (np.cos(i1) + np.cos(i2)) * rf   # TVD, positif ke bawah

    e = np.concatenate([[0.0], np.cumsum(de)])
    n = np.concatenate([[0.0], np.cumsum(dn)])
    v = np.concatenate([[0.0], np.cumsum(dv)])

    out = np.empty((depths.size, 3), dtype=float)
    out[:, 0] = np.interp(depths, fine, e)
    out[:, 1] = np.interp(depths, fine, n)
    out[:, 2] = -np.interp(depths, fine, v)   # Z elevasi = turun -> negatif
    return out


def hole_vector(az, dip):
    """Vektor satuan arah lubang (X,Y,Z) untuk azimut/dip tunggal."""
    i = (90.0 - dip) * D2R
    a = az * D2R
    return np.array([np.sin(i) * np.sin(a), np.sin(i) * np.cos(a), -np.cos(i)])


def fmt(df, cols_round):
    """Bulatkan kolom sesuai dict {kolom: desimal} untuk keluaran CSV yang rapi."""
    for c, nd in cols_round.items():
        if c in df.columns:
            df[c] = df[c].round(nd)
    return df

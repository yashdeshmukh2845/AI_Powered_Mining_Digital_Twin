# Latihan dengan GeoSuite / Training with GeoSuite

[Orebit](https://orebit.id/) · [GeoSuite](https://geosuite.orebit.id/) ·
[Build GeoSuite locally](https://github.com/ghoziankarami/geosuite/blob/main/docs/INSTALLATION.md)

## Ambil empat CSV

1. Di halaman utama GitHub, pilih **Code → Download ZIP**, lalu ekstrak.
   Untuk hanya membaca CSV atau mengimpor ke GeoSuite, Python tidak diperlukan.
2. Pilih **satu** folder pada tabel berikut. Pakai `collar.csv`, `survey.csv`,
   `assay.csv`, dan `litho.csv` dari folder yang sama.
3. Buka [GeoSuite Core](https://geosuite.orebit.id/try/Core.html), lalu tab impor
   **Import**. Pilih file sesuai jenisnya. Impor ini mengganti contoh bawaan;
   jangan campurkan file latihan dengan contoh Thalanga atau proyek lain.
4. Periksa jumlah lubang dan baris assay. Cocokkan kolom koordinat, kedalaman,
   ID lubang, kadar dan satuan sebelum melanjutkan validasi atau desurvey.

| Folder | Lubang/collar | Baris assay | Kadar utama | CRS sintetis |
| --- | ---: | ---: | --- | --- |
| `01-emas-epitermal` | 103 | 11.526 | `AU_GPT`: g/t; `AG_GPT`: g/t | EPSG:32748 |
| `02-nikel-laterit` | 350 | 8.278 | `NI_PCT`: persen; `CO_PCT`: persen | EPSG:32751 |
| `03-timah-placer` | 500 | 5.990 | `SN_KGM3`: kg/m³ | EPSG:32748 |

Semua data **sintetis**, bukan hasil eksplorasi di lokasi nyata. CRS menjelaskan
satuan dan proyeksi koordinat latihan; posisi peta tidak membuktikan lokasi
endapan. Kredit: **Orebit Synthetic Drillhole Datasets, CC BY 4.0**.

## Periksa sebelum menghitung

- `BHID` menghubungkan empat tabel. Collar harus unik untuk setiap lubang.
- `XCOLLAR`, `YCOLLAR`, `ZCOLLAR`, `TD`, `AT`, `FROM`, `TO` memakai meter.
  Elevasi positif ke atas; **DIP positif ke bawah**, 90° berarti vertikal turun.
  Jangan membalik tanda DIP tanpa menyesuaikan pengaturan impor.
- Sel kosong berarti **nilai hilang**, bukan nol. Pastikan interval punya
  `TO > FROM` dan kedalaman tidak melewati `TD`.
- `NI_PCT=1` berarti **1%**, bukan fraksi 1 atau 100%. `SN_KGM3` adalah kadar
  volumetrik; jangan diperlakukan sebagai persen atau g/t. `SG`/`BD_TM3`
  menyimpan densitas t/m³. Pertahankan satuan pada ekspor berikutnya.

Jika jumlah tidak cocok, periksa folder dan kolom pemetaan, lalu impor ulang.
Jika validasi menemukan kesalahan, baca baris yang ditunjuk dan perbaiki dulu.
Hasil desurvey, komposit, variogram dan estimasi bergantung pada pengaturan;
tabel di atas adalah pemeriksaan input, bukan angka tonase target.

Untuk latihan berikutnya, ikuti kontrol Core → Assay → Resource dalam
[manual](https://geosuite.orebit.id/docs/). Ekspor hasil Core sebelum
melanjutkan ke Assay, dan ekspor komposit Assay untuk Resource. Simpan laporan,
parameter dan file hasil agar latihan dapat diulang. Jangan menyamakan
hasil screening latihan dengan klasifikasi sumber daya untuk pelaporan publik.

## English steps

Download and extract the source ZIP. Choose one dataset folder and import its
four CSVs into Core's Import tab. Check the collar and assay counts above,
column mapping, metre units, positive-down DIP, grade units, and missing values.
Resolve validation errors before desurvey. Export Core's output for Assay,
then export Assay composites for Resource. Record processing settings and keep
exported backups. The synthetic data is suitable for teaching and testing;
this guide does not certify resource estimates or a particular release's UI.

## Verify a reproducible snapshot

CSV use needs no Python dependencies. To run integrity checks, install
`_generator/requirements.txt` in a virtual environment, then run:

```bash
python _generator/validate.py
python _generator/check_readme.py
python -m unittest discover -s tests -v
```

To package the committed CSVs without changing or regenerating them:

```bash
python _generator/package_snapshot.py --source-ref YOUR_COMMIT_SHA
```

The ZIP and checksum are in `artifacts/`. Extract the ZIP and run:

```bash
python _generator/package_snapshot.py --verify /path/to/extracted/snapshot
```

`DATA-MANIFEST.json` records file hashes, headers, row counts, generator seeds,
CRS and units. This proves the files match that manifest; it does not validate
geology or authenticate a download without a trusted source/checksum. CI keeps
a snapshot artifact for each successful check. Published releases, when
available, are separate from CI artifacts; the source ZIP remains usable.

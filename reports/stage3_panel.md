# Tahap 3 — Grid dan kelengkapan panel

Grid membentuk satu sel untuk setiap provinsi dalam 38 provinsi standar pada setiap tahun yang
diterbitkan seri. Tahun sebelum penerbitan pertama, serta tahun di antara rilis berkala yang tidak
diterbitkan, tidak dimasukkan sebagai missing. Nilai kosong di dalam tahun terbit tetap null dan
tidak diimputasi.

## Keluaran

- `data/gold/grid_provinsi.parquet`: 1.558 sel dari seri, tahun terbit, dan 38 provinsi; 243 sel
  tidak memiliki nilai.
- `data/gold/indonesia_terpisah.parquet`: 41 baris agregat Indonesia; tidak masuk denominator 38.
- `reports/tables/matriks_ketersediaan_panel.csv`: jumlah provinsi terisi, sel kosong, dan persen
  terisi per seri, tahun, dan rincian.

Persen dihitung sebagai `provinsi_terisi / 38 * 100`. Daftar lengkap angka per tahun ada di CSV
tersebut dan ringkasannya di bawah.

| Seri | Tahun terbit | Kelengkapan per tahun |
|---|---|---|
| var1311 | 2015–2024 | 2015–2019: 89,47%; 2020: 71,05%; 2021: 52,63%; 2022: 57,89%; 2023: 42,11%; 2024: 52,63% |
| var1312 | 2014, 2017, 2020, 2025 | 86,84%; 89,47%; 89,47%; 100% |
| var1410 | 2015–2025 | 2015–2023: 89,47%; 2024–2025: 100% |
| var1831 | 2015–2023 | 2015–2019: 89,47%; 2020–2023: 100% |
| var2738 | 2014, 2020 | 86,84%; 89,47% |
| var2740 | 2020–2024 | 81,58%; 57,89%; 57,89%; 68,42%; 76,32% |

`var1410` (pencatatan kelahiran anak di bawah 5 tahun) dan `var1831` (kepemilikan akta kelahiran
anak usia 0–17 tahun) dipertahankan sebagai dua seri terpisah, sesuai keputusan K-003. Kode
wilayah Indonesia `9999` disimpan terpisah. Pemekaran Papua tidak dibagikan ulang ke provinsi baru;
sel anak provinsi tanpa observasi tetap kosong sesuai susunan 38 provinsi.

Sebanyak 16 nilai nol `var1831` dipertahankan sebagai data terisi: sumber tidak mendokumentasikan
nol sebagai penanda missing. Sel kosong ditentukan dari tidak adanya observasi pada pasangan
provinsi-tahun. Rincian keputusan dan jumlah sel terdampak per seri tercatat pada K-008 sampai
K-017 di `log-keputusan.csv`.

Reproduksi: `python -m src.silver.buat_silver`, lalu `python -m src.gold.grid_provinsi` (atau
`python pipeline.py`).

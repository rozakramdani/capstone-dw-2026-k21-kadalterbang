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
- `reports/tables/calon_anomali.csv`: 71 kandidat lintas snapshot dengan kategori dan penjelasan.
- `reports/tables/perbandingan_snapshot.csv` dan `revisi_snapshot.csv`: pembandingan versi dan
  perubahan nilai; tidak ada revisi nilai antar-snapshot pada data ini.
- `reports/tables/patahan_seri.csv`: dua indikasi perubahan serentak pada var1410.

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
provinsi-tahun.

## Snapshot, anomali, dan patahan

Silver menyimpan 1.988 baris BPS untuk enam seri utama setelah menghapus salinan CSV/JSON dalam
snapshot yang sama. Silver keseluruhan juga memuat 14 baris WDI pembanding, sehingga totalnya 2.002
baris; rincian integrasi ada di `reports/tahap5_penyimpanan.md`.
Pengamatan pada tanggal snapshot berbeda tetap dipertahankan sekalipun nilainya sama; jika nilainya
berbeda, keduanya dicatat sebagai revisi. Empat seri yang tersedia pada 17 dan 20 Oktober memiliki
632 observasi sama dan 0 nilai berubah. `var1410` dan `var1831` hanya tersedia pada snapshot
20 Oktober. Grid menggunakan snapshot terbaru per seri. Profil mencakup semua snapshot; kandidat
dari nilai sama yang muncul pada tanggal berbeda tetap menjadi baris terpisah dengan tanggal
snapshot masing-masing.

Semua 71 calon anomali lintas snapshot mendapat kategori: 70 `outlier_asli` dan 1 `patahan_seri`;
tidak ada `galat_input` yang terverifikasi sehingga tidak ada nilai yang dikoreksi. Sebanyak 13
kandidat var1311 muncul pada kedua snapshot karena nilainya sama, tetapi tetap dilaporkan sebagai
dua observasi versi yang berbeda. Enam belas nol `var1831` dicocokkan dengan ekspor sumber dan tetap
dipertahankan sebagai observasi, bukan diubah menjadi missing.

Saringan patahan menandai tahun jika sekurangnya 95% provinsi yang dapat dibandingkan bergerak
searah dan perubahan median absolut mencapai 3% dari median tahun sebelumnya. Saringan menemukan
indikasi pada `var1410` tahun 2020 dan 2022; sumber tidak mengonfirmasi perubahan definisi/metode,
maka keduanya hanya ditandai, tidak diperbaiki. Satu kandidat anomali `var1410` pada 2020 masuk
kategori `patahan_seri`.

Aturan snapshot, kategori, alasan, dan jumlah baris terdampak dirinci pada K-018 sampai K-021 di
`log-keputusan.csv`.

Reproduksi: `python -m src.silver.buat_silver`, lalu `python -m src.gold.grid_provinsi` (atau
`python pipeline.py`).

# Tahap 5: Penyimpanan

## Pilihan basis data

SQLite menyimpan seluruh tabel dalam satu berkas tanpa server dan dapat dijalankan melalui
pustaka standar Python, sehingga mudah direproduksi untuk skala data proyek ini. DDL empat
tabel ada di `src/gold/skema_sql.sql`; kolom numerik, teks, integer, dan nilai nullable
dinyatakan secara eksplisit. Kunci primer mengikuti grain tiap tabel: sumber/seri/wilayah/
periode/rincian/berkas untuk Silver, wilayah/periode/seri untuk panel, dan periode/seri
untuk tabel nasional serta rekonsiliasi.

SQLite dipilih untuk prototipe dan alur kerja lokal, bukan sebagai klaim bahwa ia terbaik
untuk semua skala. DuckDB lebih sesuai bila analisis kolumnar besar dan kueri langsung ke
Parquet menjadi prioritas. PostgreSQL lebih sesuai bila banyak pengguna perlu menulis
bersamaan, mengakses basis data melalui server, atau memerlukan operasi terkelola.

## Tabel terstruktur dibanding JSON mentah

Respons JSON mentah tetap dipertahankan sebagai Bronze: format dokumen menjaga
bentuk dan metadata asli sumber, serta lebih fleksibel bila struktur API berubah. Namun,
struktur yang bervariasi membuat validasi tipe, konsistensi nama kolom, kunci unik, dan
kueri lintas seri/wilayah/periode lebih sulit; struktur SQL memberi tipe dan batasan
kunci yang eksplisit sehingga data siap diprofilkan dan dianalisis. Karena itu JSON mentah
dipakai untuk arsip/lineage, sementara tabel SQLite bertipe dipakai untuk Silver dan Gold,
bukan sebagai pengganti arsip.

## Pemuat dan verifikasi

Jalankan pipeline setelah data mentah tersedia:

```bash
python pipeline.py
```

Pipeline membentuk Silver, panel, tabel nasional, lalu memuat Silver dan Gold beserta
`reports/tables/rekonsiliasi_nasional.csv` ke `data/gold/warehouse.sqlite3`. Pemuatan
memvalidasi skema Silver, kunci unik setiap tabel, flag ketersediaan panel, menjalankan
penggantian isi secara transaksional, dan membandingkan jumlah baris SQL dengan artefak
masing-masing. Hasil uji pipeline: 2.002 baris Silver, 1.558 panel, 55 nasional, dan 55
rekonsiliasi. Berkas SQLite diabaikan Git dan dapat dibangun ulang.

Silver mencakup 1.988 baris BPS dan 14 baris WDI; laporan Tahap 3 yang menyebut 1.988
hanya menghitung seri BPS. Tidak ada baris yang hilang atau ganda pada pemuatan SQL.

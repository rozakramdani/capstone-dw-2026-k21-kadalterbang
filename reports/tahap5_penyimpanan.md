# Draf laporan tim — Tahap 5: Penyimpanan

## Pilihan basis data

Untuk pemuatan pertama Silver, tim memilih SQLite. SQLite menyimpan tabel dalam satu
berkas tanpa server dan dapat dijalankan melalui pustaka standar Python, sehingga mudah
direproduksi dan dibagikan untuk skala data proyek ini. DDL di
`src/silver/skema_silver.sql` menyatakan tipe setiap kolom, mewajibkan nilai terisi, dan
memakai kunci primer gabungan yang sama dengan kunci unik Silver: sumber, seri, wilayah,
periode, rincian, dan berkas sumber. Kolom lineage tetap menjadi bagian dari tabel agar
setiap observasi dapat ditelusuri ke snapshot mentah.

SQLite dipilih untuk prototipe dan alur kerja lokal, bukan sebagai klaim bahwa ia terbaik
untuk semua skala. DuckDB lebih sesuai bila analisis kolumnar besar dan kueri langsung ke
Parquet menjadi prioritas. PostgreSQL lebih sesuai bila banyak pengguna perlu menulis
bersamaan, mengakses basis data melalui server, atau memerlukan operasi terkelola.

## Tabel terstruktur dibanding JSON mentah

Respons JSON mentah sebaiknya tetap dipertahankan sebagai Bronze: format dokumen menjaga
bentuk dan metadata asli sumber, serta lebih fleksibel bila struktur API berubah. Namun,
struktur yang bervariasi membuat validasi tipe, konsistensi nama kolom, kunci unik, dan
kueri lintas seri/wilayah/periode lebih sulit; struktur SQL memberi tipe dan batasan
kunci yang eksplisit sehingga data siap diprofilkan dan dianalisis. Karena itu tabel
SQLite adalah representasi Silver untuk analisis, bukan pengganti arsip JSON mentah.

## Pemuat dan uji awal

Jalankan setelah Silver Parquet tersedia:

```bash
python -m src.silver.muat_silver_sql
```

Pemuat memvalidasi skema Silver, mengganti isi tabel dalam satu transaksi, dan melaporkan
jumlah baris yang dimuat. Berkas SQLite baku berada di
`data/silver/silver.sqlite3` (tidak perlu di-commit; tabel dapat dibuat ulang dari
Parquet). Uji 22 November 2026 berhasil dua kali berturut-turut: 2.002 baris dimuat,
sesuai jumlah kunci unik, tanpa kunci duplikat. Angka ini berbeda dari ringkasan 1.988
baris di `reports/stage3_panel.md`; laporan Tahap 3 perlu direkonsiliasi dengan Silver
terkini.

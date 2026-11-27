## Danil (124450103) - Sprint 1
- **Alat:** Gemini/ChatGPT
- **Bagian:** Menyusun sintaks Pandas untuk deteksi outlier (IQR & Z-Score) dan visualisasi Seaborn (Boxplot/Lineplot).
- **Verifikasi:** Saya mengecek langsung file CSV yang dihasilkan dan membuka gambar grafik untuk memastikan tidak ada data yang salah plot.


## Bimo (124450113) - Sprint 1
- **Alat:** GitHub Copilot (agent)
- **Bagian:** DDL SQLite, pemuat Silver ke SQLite, draf alasan pilihan basis data (tahap 5).
- **Verifikasi:** Membaca seluruh kode, menjalankan pemuat dengan .venv, mencocokkan 2.002 baris dengan silver.parquet, dan membuktikan selisih dengan 1.988: 1.988 baris BPS + 14 baris WDI = 2.002.


## Bimo (124450113) - Sprint 2
- **Alat:** GitHub Copilot (agent)
- **Bagian:** src/gold/rekonsiliasi.py, pemanggilan di pipeline.py, draf laporan tahap 6.
- **Verifikasi:** Membaca kode, mengecek metadata WDI (sourceNote) dan BPS var1410 (anak <5 tahun, Susenas, akta), menjalankan pipeline, dan mengubah median agar hanya var1410.
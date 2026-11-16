# Laporan Tahap 2: Profil dan Calon Anomali (Sprint 1)

**Penanggung Jawab:** Danil Nur Fadillah (124450103)

## 1. Tujuan
Melakukan profiling data mentah hasil ekstraksi untuk 6 seri (var1311, var1312, var2738, var2740, var1410, var1831), menemukan statistik deskriptif, dan menandai calon anomali tanpa melakukan perbaikan (imputasi/penghapusan).

## 2. Metodologi
- **Pemisahan Wilayah:** Baris Indonesia (kode 9999) dipisahkan dari perhitungan statistik provinsi agar tidak bias.
- **Pembersihan Dasar:** Nilai kosong (NaN) di-drop khusus untuk perhitungan statistik.
- **Deteksi Anomali:** Menggunakan dua metode, yaitu IQR (di luar 1.5 *Interquartile Range*) dan Z-Score (nilai absolut > 3).
- **Visualisasi:** Boxplot per periode dan deret waktu (time series) per provinsi.

## 3. Ringkasan Statistik per Seri
*(Tuliskan ringkasan dari file `reports/tables/profil_seri.csv` di sini. Contoh:)*
- Seri **var1311** memiliki ... baris data dengan rentang nilai ... hingga ....
- Seri **var1312** memiliki ... baris data dengan rentang nilai ... hingga ....
*(dst...)*

## 4. Daftar Calon Anomali
Berdasarkan deteksi IQR dan Z-Score, ditemukan beberapa titik data ekstrem. Daftar lengkap dapat dilihat di `reports/tables/calon_anomali.csv`. 
*(Sebutkan 1-2 contoh anomali jika ada, misal: "Provinsi X pada tahun Y memiliki nilai Z-score > 3").*

## 5. Visualisasi
*(Sisipkan gambar menggunakan markdown, contoh:)*
![Boxplot var1311](gambar/boxplot_var1311.png)
![Deret Waktu var1311](gambar/deret_waktu_var1311.png)

**Catatan:** Sesuai instruksi, pada tahap ini belum dilakukan perbaikan, imputasi, atau penghapusan data. Data ekstrem hanya ditandai untuk dianalisis lebih lanjut pada tahap pembersihan/Silver.
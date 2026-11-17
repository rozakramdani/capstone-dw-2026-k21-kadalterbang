# Laporan Tahap 2: Profil dan Calon Anomali (Sprint 1)

**Penanggung Jawab:** Danil Nur Fadillah (124450103)

## 1. Tujuan
Melakukan profiling data mentah hasil ekstraksi untuk 6 seri utama (var1311, var1312, var2738, var2740, var1410, var1831), menemukan statistik deskriptif, dan menandai calon anomali tanpa melakukan perbaikan (imputasi/penghapusan) pada tahap ini.

## 2. Metodologi
- **Pemisahan Wilayah:** Baris agregat Indonesia (kode wilayah 9999) dipisahkan dari perhitungan statistik tingkat provinsi agar tidak bias.
- **Pembersihan Dasar:** Nilai kosong (NaN) di-drop secara spesifik untuk keperluan perhitungan statistik (bukan menghapus data di Silver).
- **Deteksi Anomali:** Menggunakan dua metode sekaligus, yaitu IQR (nilai di luar 1.5 *Interquartile Range*) dan Z-Score (nilai absolut > 3).
- **Visualisasi:** Membuat boxplot per periode dan deret waktu (time series) per provinsi untuk melihat sebaran dan tren data.

## 3. Ringkasan Statistik per Seri
Berdasarkan hasil pemrosesan script `profil_anomali.py`, berikut adalah ringkasan statistik dari masing-masing seri (diambil dari `reports/tables/profil_seri.csv`):

- Seri **var1311** memiliki **1.100** baris data dengan rentang nilai **0.0** hingga **0.3** (rata-rata 0.069).
- Seri **var1312** memiliki **556** baris data dengan rentang nilai **34.28** hingga **91.92** (rata-rata 69.29).
- Seri **var2738** memiliki **268** baris data dengan rentang nilai **34.37** hingga **81.66** (rata-rata 55.21).
- Seri **var2740** memiliki **520** baris data dengan rentang nilai **0.35** hingga **100.0** (rata-rata 58.97).
- Seri **var1410** memiliki **764** baris data dengan rentang nilai **17.44** hingga **97.7** (rata-rata 75.09).
- Seri **var1831** memiliki **644** baris data dengan rentang nilai **0.0** hingga **98.78** (rata-rata 81.16).

## 4. Daftar Calon Anomali
Berdasarkan deteksi menggunakan metode IQR dan Z-Score, ditemukan beberapa titik data ekstrem di tingkat provinsi. Daftar lengkap beserta nilai dan alasannya dapat dilihat pada file `reports/tables/calon_anomali.csv`. 

Berikut adalah beberapa contoh temuan anomali yang paling mencolok:

1. **Nilai 0.0 pada Provinsi Baru (Seri var1831):**
   Ditemukan banyak nilai **0.0** pada seri `var1831` di wilayah pemekaran baru seperti **Papua Tengah, Papua Selatan, Papua Pegunungan, dan Papua Barat Daya**. Nilai ini ditandai oleh IQR dan Z-Score. Mengingat seri ini mengukur pencatatan kelahiran, nilai 0% sangat tidak wajar dan kemungkinan besar merupakan *missing value* yang dikodekan sebagai 0 oleh sumber data. Nilai ini **tidak diubah** pada tahap ini, melainkan dicatat untuk penanganan khusus di Tahap 3 (Pembersihan).

2. **Nilai Ekstrem Rendah pada var1410:**
   Pada seri `var1410` (Pencatatan Kelahiran), Provinsi **Papua Pegunungan** memiliki nilai **17.44** yang sangat jauh di bawah rata-rata nasional (75.09) dan ditandai oleh IQR serta Z-Score. Hal ini menunjukkan disparitas layanan pencatatan sipil yang sangat tinggi di wilayah tersebut.

3. **Nilai Ekstrem Tinggi pada var1311:**
   Pada seri `var1311` (Korban Kejahatan Kekerasan), Provinsi **Papua** dan **Papua Barat** secara konsisten memiliki nilai tertinggi (mencapai 0.3) yang ditandai sebagai anomali oleh IQR dan Z-Score dibandingkan provinsi lain yang rata-rata berada di bawah 0.1.

**Catatan Penting:** Sesuai dengan prinsip kerja Capstone, anomali di atas **tidak dihapus atau diperbaiki**, melainkan hanya ditandai (flagging) sebagai bahan pertimbangan pada tahap pembersihan dan analisis selanjutnya.

## 5. Visualisasi
Berikut adalah contoh visualisasi (boxplot dan deret waktu) yang telah di-generate dan disimpan di folder `reports/gambar/`. Semua seri (var1311 s.d. var1831) memiliki gambar masing-masing.

**Boxplot:** Menunjukkan sebaran nilai antarprovinsi di setiap periode, memudahkan untuk melihat adanya nilai yang jauh menyimpang (outlier).
![Boxplot var1311](gambar/boxplot_var1311.png)

**Deret Waktu:** Menunjukkan tren nilai per provinsi dari tahun ke tahun. Garis merah tebal adalah nilai median provinsi.
![Deret Waktu var1311](gambar/deret_waktu_var1311.png)

**Catatan:** Sesuai dengan prinsip kerja Capstone, pada tahap ini belum dilakukan perbaikan, imputasi, atau penghapusan data. Data ekstrem hanya ditandai (flagging) murni untuk tujuan eksplorasi.
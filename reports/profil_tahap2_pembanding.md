# Profil Seri Pembanding WDI (Tahap 2)

**Penanggung Jawab:** Danil Nur Fadillah (124450103)

## 1. Tabel Ketersediaan
Data profil ketersediaan seri pembanding dari World Bank (WDI) telah berhasil diekstrak dan disimpan dalam file `reports/tables/profil_pembanding_wdi.csv`.

Berdasarkan hasil ekstraksi data WDI:
- **VC.IHR.PSRC.P5** (Intentional homicides per 100,000): Tersedia dari tahun **1998 hingga 2022**.
- **SP.REG.BRTH.ZS** (Birth registration under 5): Tersedia dari tahun **2002 hingga 2021**.

## 2. Kandidat Rincian yang Sebanding (untuk Tahap 6)
Berdasarkan hasil profiling, berikut adalah analisis kandidat untuk rekonsiliasi di Tahap 6:

1. **Seri Pencatatan Kelahiran (SP.REG.BRTH.ZS vs var1410/var1831)**
   - **Rincian WDI:** Mengukur persentase anak di bawah 5 tahun yang tercatat kelahirannya.
   - **Kandidat Sebanding:** BPS `var1410` (kelompok umur balita/<5 tahun). *Catatan: `var1831` tidak disatukan karena berbeda kelompok umur.*
   - **Alasan:** Konsep dan kelompok umur sebanding, sehingga bisa dibandingkan langsung untuk melihat selisih (gap) antara data BPS dan standar internasional.
   - **Tahun Beririsan:** **2015 hingga 2021**.

2. **Seri Korban Kekerasan (VC.IHR.PSRC.P5 vs var1311)**
   - **Rincian WDI:** Mengukur jumlah pembunuhan yang disengaja (intentional homicides) per 100.000 penduduk.
   - **Kandidat Sebanding:** BPS `var1311` (Persentase korban kejahatan kekerasan).
   - **Alasan:** **Definisi Berbeda**. WDI mengukur insiden pembunuhan per 100.000 orang, sedangkan BPS mengukur persentase korban kekerasan. Seri ini tidak bisa dibandingkan secara langsung, melainkan hanya sebagai konteks (sesuai panduan kelompok).
   - **Tahun Beririsan:** **2015 hingga 2022**.
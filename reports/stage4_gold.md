# Tahap 4 — Aturan pemilihan Gold

Fungsi `pilih_observasi_gold` di `src/gold/grid_provinsi.py` dipanggil melalui
`bentuk_grid` oleh `pipeline.py`. Ia memilih satu observasi untuk setiap indikator, wilayah, dan
tahun sebelum membentuk grid provinsi lengkap. Aturan dan jumlah baris Silver yang tidak terpilih
dicatat pada K-024–K-027 di `log-keputusan.csv`; hitungan aktual juga ditulis ke
`reports/tables/pemilihan_gold.csv`.

## Aturan

1. **Snapshot:** untuk setiap seri gunakan tanggal snapshot terbaru, sama untuk keenam seri.
   Jika nilai versi berbeda, versi terbaru menang; versi lama tetap di Silver dan tidak dirata-rata.
2. **Rincian:** panel memilih rincian `Tidak ada` untuk `var1311`, `var1312`, `var1410`, `var1831`,
   `var2738`, dan `var2740`. Rincian lain tetap di Silver, tidak dijadikan baris indikator Gold.
   Jika rincian panel yang ditetapkan tidak ditemukan, pipeline berhenti dengan error.
3. **Periode:** nilai tahunan dipertahankan langsung. Jika hanya tersedia periode semesteran,
   triwulanan, atau bulanan, Gold menggunakan rerata aritmetika periode yang tersedia untuk
   provinsi-tahun tersebut; subperiode kosong tidak diimputasi. Jika tersedia nilai tahunan dan
   sub-tahunan sekaligus, nilai tahunan diprioritaskan. Sumber dan jumlah periode penyusun
   dipertahankan pada kolom `periode_sumber` dan `jumlah_periode_sumber`.
4. **Flagging:** kategori kandidat, `flag_outlier`, `flag_galat_input`, dan `flag_patahan_seri`
   dibawa ke Gold. Tahun patahan ditandai pada seluruh observasi wilayah terkait, tanpa menghapus
   nilai. Kolom `flag_kandidat_anomali` menandai baris kandidat yang diprofilkan.
5. **Kunci:** grid provinsi unik pada `(seri_kode, wilayah_kode, periode)`. Sel tanpa nilai
   observasi dibuat sebagai null saat grid lengkap dibentuk. Agregat Indonesia berada di berkas
   terpisah dan tidak dihitung sebagai provinsi.

## Hasil pada data saat ini

- Dari 2.002 baris total Silver, enam seri panel BPS berisi 1.988 baris. Pemilihan snapshot terbaru
  meninggalkan **632 baris snapshot lama** untuk seri tersebut di Silver; 1.356 observasi dari
  snapshot terbaru menjadi masukan Gold. Empat belas baris WDI pembanding tetap di Silver dan tidak
  masuk panel provinsi.
- Semua seri saat ini hanya memiliki rincian `Tidak ada`: **0 baris** dikeluarkan karena rincian.
- Data periode kasus seluruhnya tahunan: **0 baris** dikeluarkan karena prioritas tahunan dan
  **0 baris** periode sub-tahunan digabung.
- Grid panel memiliki 1.558 sel, termasuk 243 sel kosong. Sebanyak 41 agregat Indonesia tersimpan
  terpisah.
- Gold membawa **58 kandidat anomali**. Flag patahan mencakup 68 sel provinsi-tahun (var1410 pada
  2020 dan 2022) serta dua baris agregat Indonesia terkait.

Validasi pipeline memastikan kunci grid tidak berulang. Kelengkapan per seri tetap tersedia sebagai
tabel tersendiri di `reports/tables/matriks_ketersediaan_panel.csv`.

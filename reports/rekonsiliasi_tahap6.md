# Persiapan Tahap 6 — Rekonsiliasi nasional

## Tabel nasional periode × seri

`reports/tables/rekonsiliasi_nasional.csv` berisi baris Indonesia (`wilayah_kode=9999`)
dari `data/silver/silver.parquet`, satu baris per periode dan seri. Tabel mencakup enam
seri utama BPS dan dua seri pembanding WDI. Untuk tiap seri dipakai snapshot terbaru yang
ada di Silver; berkas mentah dan SHA-256 tetap dicatat di setiap baris.

Nilai kosong pada sumber WDI tidak menjadi observasi dan karena itu tidak ditambahkan.
Periode irisan di bawah dihitung dari tahun dengan nilai nasional teramati pada kedua seri,
bukan dari irisan rentang minimum–maksimum ketersediaan.

## Pasangan rekonsiliasi

| Seri utama nasional | Seri pembanding nasional | Periode bersama teramati | Kategori dan catatan keterbandingan |
|---|---|---|---|
| BPS `var1410` — proporsi anak di bawah 5 tahun yang kelahirannya dicatat lembaga pencatatan sipil | WDI `SP.REG.BRTH.ZS` — completeness of birth registration | 2016, 2017, 2018, 2021 (4 periode) | **Konsep/kelompok umur sebanding:** metadata BPS menyebut anak berumur di bawah 5 tahun; catatan WDI menyebut anak *under age 5*. WDI menghitung persentase anak yang kelahirannya tercatat saat survei; bukti dapat berupa sertifikat yang dilihat pewawancara atau keterangan ibu/pengasuh. Bandingkan sebagai seri nasional sekelompok umur sama, tetapi jangan menganggap metode pengumpulan dan nilai antar-sumber identik. |
| BPS `var1311` — proporsi penduduk korban kejahatan kekerasan dalam 12 bulan terakhir | WDI `VC.IHR.PSRC.P5` — intentional homicides per 100,000 people | 2022 (1 periode) | **Definisi berbeda:** BPS mengukur persentase penduduk yang menjadi korban kejahatan kekerasan; WDI mengukur kematian akibat pembunuhan disengaja per 100.000 penduduk. Nilainya tidak sebanding langsung; WDI hanya disertakan sebagai konteks. |

Sebagai pemeriksaan bahwa kelompok umur tidak tertukar, seri BPS `var1831` berjudul
“Persentase Anak Berumur 0-17 Tahun yang Memiliki Akta Kelahiran”. Seri tersebut bukan
pasangan pengganti `var1410` dan tidak digabungkan dengan seri balita.

## Ringkasan metrik

- `pasangan_rekonsiliasi=2`: dua pasangan yang ditetapkan panduan kelompok.
- `periode_beririsan=5`: empat periode bersama untuk pasangan pencatatan kelahiran dan satu
  periode bersama untuk pasangan kekerasan/pembunuhan (dihitung sebagai pasangan-periode).
- Rentang tahun saja akan melebihkan irisan: observasi WDI tidak tersedia pada setiap tahun
  di antara tahun pertama dan terakhir.

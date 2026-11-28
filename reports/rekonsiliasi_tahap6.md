# Tahap 6 — Rekonsiliasi seri nasional

Pipeline membangun `data/gold/rekonsiliasi_nasional.parquet` dari
`data/gold/tabel_nasional.parquet`. Setiap baris berisi periode, kode kedua seri,
nilai dan satuan dari masing-masing sumber, selisih bertanda (`nilai_utama -
nilai_pembanding`), kategori penjelasan, catatan, serta lineage kedua nilai jika
tersedia. Join memakai seluruh periode dari kedua seri, sehingga periode tanpa
pasangan tetap disimpan. Nilai dan selisih tidak dihapus atau disesuaikan.
Hasil saat ini berisi 30 baris: 5 periode berpasangan dan 25 periode tanpa pasangan.
Empat irisan `var1410`/WDI ada pada 2016, 2017, 2018, dan 2021; satu irisan
`var1311`/WDI ada pada 2022.

## Pasangan yang ditetapkan

| Seri utama | Pembanding | Kategori untuk periode berpasangan | Penjelasan |
|---|---|---|---|
| BPS `var1410` — pencatatan kelahiran anak balita | WDI `SP.REG.BRTH.ZS` | **metode berbeda** | Kelompok umur sama-sama anak di bawah 5 tahun. Metadata BPS menyebut sumber Susenas serta pencatatan kelahiran yang dibuktikan dengan akta. Catatan WDI juga menetapkan anak di bawah 5 tahun, berdasarkan survei rumah tangga; bukti pencatatan dapat berupa sertifikat yang dilihat pewawancara atau keterangan ibu/pengasuh. Umur sebanding, tetapi bukti dan metode pengukurannya tidak identik. |
| BPS `var1311` — proporsi penduduk korban kejahatan kekerasan | WDI `VC.IHR.PSRC.P5` — pembunuhan disengaja per 100.000 penduduk | **definisi berbeda** | BPS menghitung proporsi penduduk korban kejahatan kekerasan dalam 12 bulan, sedangkan WDI menghitung laju kematian akibat pembunuhan disengaja per 100.000 penduduk. WDI ditampilkan sebagai konteks, bukan ukuran yang sebanding. |

Pemeriksaan kelompok umur dilakukan pada judul dan definisi BPS `var1410` di berkas
JSON indikator BPS serta `sourceNote` WDI `SP.REG.BRTH.ZS` di metadata indikator
WDI. Keduanya menyatakan kelompok di bawah 5 tahun. Pemeriksaan metode juga mencakup
catatan sumber Susenas BPS dan catatan survei rumah tangga WDI. Kategori
**belum terjelaskan** tidak digunakan karena kedua pasangan memiliki perbedaan yang
dapat dijelaskan dari metadata tersebut; karena itu kolom dugaan dan bukti yang
dicari kosong.

Kolom selisih tetap dihitung secara aritmetis ketika kedua angka tersedia, termasuk
untuk pasangan definisi berbeda. Satuan ada pada kolom terpisah agar selisih angka
yang tidak sebanding tidak disalahartikan sebagai ukuran substantif.

`results/124450113/metrics.json` memuat `pasangan_rekonsiliasi=2` dan
`selisih_median=0.03`, yaitu median selisih bertanda dari empat periode berpasangan
var1410 vs SP.REG.BRTH.ZS (satuan sama, persen). Selisih var1311 vs VC.IHR.PSRC.P5
tidak dimasukkan ke median karena membandingkan persen dengan per 100.000 penduduk.
Selisih 2017 (-4,72 poin) menonjol; dugaan: perbedaan bukti pencatatan (akta vs
keterangan ibu) dan sumber survei WDI, belum dibuktikan.

Catatan penyimpanan: tabel SQL `rekonsiliasi_nasional` di SQLite masih dimuat dari
`reports/tables/rekonsiliasi_nasional.csv` (Sprint 1). Pemuatan
`data/gold/rekonsiliasi_nasional.parquet` ke SQL dijadwalkan di PR berikutnya.

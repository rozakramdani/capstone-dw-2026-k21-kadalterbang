# Laporan Tim Kadal Terbang — Kasus 21: Keamanan dan Pencatatan Sipil

Laporan ini merangkum hasil yang sudah tersedia di repo. Temuan angka dirujuk ke Silver, Gold,
tabel profil, atau `log-keputusan.csv`; pekerjaan yang belum punya bukti keluaran ditandai sebagai
keterbatasan, bukan dianggap selesai.

## Ringkasan

Kasus 21 mengolah enam seri utama BPS tingkat provinsi untuk SDG 16 (`var1311`, `var1312`,
`var2738`, `var2740`, `var1410`, `var1831`) dan dua pembanding nasional WDI
(`VC.IHR.PSRC.P5`, `SP.REG.BRTH.ZS`). Temuan utama adalah celah observasi di panel provinsi,
beberapa nilai ekstrem yang tetap valid menurut sumber, dua indikasi perubahan serentak pada
`var1410`, serta tidak ditemukannya revisi nilai pada observasi BPS yang berpasangan antar-snapshot.
Perbandingan kelahiran hanya memiliki empat tahun observasi bersama; seri kekerasan dan pembunuhan
berbeda definisi dan dipakai sebagai konteks, bukan sebagai selisih langsung.

## Data dan lineage

Paket kasus 21 menyediakan data BPS dan WDI yang diambil pada 17–20 Oktober 2026. Data BPS
mencakup CSV/JSON dan manifest asal; data WDI mencakup JSON data serta metadata indikator.
Catatan Sprint 1 mencatat 26 berkas mentah cocok dengan `data/raw/MANIFEST.csv`, menghasilkan
4.261 baris ekstraksi. `data/raw/` tidak disimpan di repo; data dapat diunduh kembali dengan
`python unduh_data.py --kasus 21`.

Pembaca ekstraksi menambahkan `_berkas_raw` dan `_sha256_raw` pada setiap baris. Nilai hash diambil
dari manifest dengan `src.common.manifest`, bukan ditulis manual. Pipeline memeriksa hash berkas
dan memastikan seluruh jalur di manifest berhasil dibaca. Silver saat ini berisi 2.002 baris,
delapan seri, 39 kode wilayah (38 provinsi dan Indonesia), serta 11 berkas sumber yang menghasilkan
observasi. Struktur ini mempertahankan sumber, periode, rincian, satuan, dan lineage tanpa
mencampurkan nilai BPS dan WDI.

Snapshot mentah yang tersedia adalah paket Oktober 2026; tidak ada catatan penarikan API baru yang
independen dari snapshot tersebut. Atribusi data mengikuti `data/LISENSI.md`: Badan Pusat Statistik
dan World Bank, World Development Indicators. Lisensi basis data turunan mengikuti ODbL 1.0.

### Penyimpanan SQL dan lineage

`python pipeline.py` memuat empat tabel SQLite ke `data/gold/warehouse.sqlite3` setelah seluruh
Parquet dan tabel rekonsiliasi terbentuk. DDL bertipe eksplisit ada di `src/gold/skema_sql.sql`:
`silver_observasi` (PK sumber-seri-wilayah-periode-rincian-berkas), `panel_provinsi` (PK
wilayah-periode-seri), `tabel_nasional` dan `rekonsiliasi_nasional` (PK periode-seri).
Panel menyimpan nilai kosong sebagai SQL `NULL` dan flag ketersediaan/anomali sebagai integer
boolean. Setiap pemuatan mengganti isi tabel dalam satu transaksi dan memverifikasi jumlah baris
SQL terhadap artefak sumbernya.

Pada keluaran kasus ini, SQLite memuat 2.002 baris Silver, 1.558 baris panel Gold, 55 baris
tabel nasional, dan 55 baris rekonsiliasi; jumlah setiap tabel sama dengan Parquet Silver/panel/
tabel nasional atau CSV rekonsiliasi yang bersangkutan. SQLite cocok untuk skala proyek dan
pipeline lokal karena tidak membutuhkan server dan dapat direproduksi dengan pustaka standar.
Tabel bertipe dan PK eksplisit memudahkan pemeriksaan kunci, konsistensi tipe, serta kueri
lintas seri/wilayah/periode; DuckDB lebih tepat bila prioritasnya analitik kolumnar besar atau
kueri langsung Parquet, sedangkan PostgreSQL lebih sesuai untuk banyak penulis dan layanan
bersamaan.

JSON mentah tetap dipertahankan sebagai Bronze karena mempertahankan bentuk respons dan metadata
asli saat format sumber berubah. Namun, skema JSON yang bervariasi tidak memberi batasan tipe dan
kunci relasional setegas SQL, sehingga kurang praktis untuk validasi dan analisis tabel. Pilihan
ini sengaja berlapis: dokumen mentah untuk arsip/lineage, SQL bertipe untuk Silver dan Gold yang
telah dinormalisasi. Berkas SQLite merupakan keluaran turunan, tidak di-commit; tabel dapat
dibangun ulang dari artefak repo dan data mentah.

## Masalah data dan penanganannya

### Celah panel

Gold membentuk grid 38 provinsi hanya untuk periode yang diterbitkan tiap seri. Dari 1.558 sel
seri × periode × provinsi, 243 tidak memiliki observasi; sel dibiarkan kosong, bukan diisi nol atau
diimputasi. Tahun sebelum seri terbit dan tahun yang tidak diterbitkan pada seri berkala tidak
dihitung sebagai missing.

| Seri | Periode terbit | Sel panel | Kosong |
|---|---|---:|---:|
| `var1311` | 2015–2024 | 380 | 105 |
| `var1312` | 2014, 2017, 2020, 2025 | 152 | 13 |
| `var1410` | 2015–2025 | 418 | 36 |
| `var1831` | 2015–2023 | 342 | 20 |
| `var2738` | 2014, 2020 | 76 | 9 |
| `var2740` | 2020–2024 | 190 | 60 |
| **Total** |  | **1.558** | **243** |

Kesenjangan terbesar ada pada `var1311` (105 sel) dan `var2740` (60 sel). Indonesia (`9999`)
dipisahkan dari denominator provinsi. Wilayah diselaraskan ke 38 provinsi; nilai Papua induk tidak
dibagi ke provinsi hasil pemekaran karena sumber tidak menyediakan dasar pembagian (K-001,
K-010–K-016).

### Anomali dan patahan

Profil IQR dan Z-score menandai 71 kandidat anomali lintas snapshot: 70 `outlier_asli`,
1 `patahan_seri`, dan tidak ada `galat_input` terverifikasi (K-004, K-019, K-020). Contoh nilai
ekstrem adalah `var1410` Papua Pegunungan 17,44 pada 2024. Sebanyak 16 nilai nol `var1831` pada
provinsi baru Papua cocok dengan ekspor sumber dan tidak didokumentasi sebagai sentinel missing;
semuanya dipertahankan sebagai observasi (K-017). Kandidat ditandai, tidak dihapus atau dikoreksi.

Saringan patahan menandai `var1410` pada 2020 dan 2022. Pada masing-masing tahun 34 provinsi
dibandingkan dan 97,06% bergerak searah. Median berubah 2,745 poin (3,66% relatif) pada 2020 dan
3,94 poin (5,00%) pada 2022. Ambang saringan adalah sekurangnya 95% provinsi searah dan perubahan
median relatif sekurangnya 3%. Ini indikasi perubahan serentak, bukan bukti perubahan metode;
nilai dipertahankan. Kandidat Nusa Tenggara Timur tahun 2020 masuk kategori `patahan_seri`
(K-021).

### Snapshot dan revisi

Deduplikasi hanya menghapus salinan CSV/JSON dengan kunci pengamatan dan tanggal snapshot sama;
snapshot berbeda dipertahankan sebagai versi (K-005, K-008, K-018). Untuk empat seri BPS yang
tersedia di kedua snapshot, 632 observasi berpasangan memiliki nilai sama dan tidak ada revisi
nilai. `var1410` dan `var1831` hanya tersedia pada snapshot 20 Oktober. Hasil pembandingan ada di
`reports/tables/perbandingan_snapshot.csv` dan `reports/tables/revisi_snapshot.csv`.

### Koreksi katalog

Katalog awal diperiksa terhadap judul tabel BPS dan metadata WDI, lalu satuan dan kode SDG
dikoreksi (K-022).

| Seri | Kode SDG | Satuan |
|---|---|---|
| `var1311` | 16.1.3 | persen |
| `var1312` | 16.1.4 | persen |
| `var2738` | 16.2.1 | persen |
| `var2740` | 16.3.1 | persen |
| `var1410` | 16.9.1 | persen |
| `var1831` | 16.9.1 | persen |
| `VC.IHR.PSRC.P5` | 16.1.1 | per 100.000 penduduk |
| `SP.REG.BRTH.ZS` | 16.9.1 | persen |

### Penelusuran angka

Jumlah sel dan missing dapat ditarik dari `data/gold/grid_provinsi.parquet` dan
`reports/tables/matriks_ketersediaan_panel.csv`; kandidat dari `reports/tables/calon_anomali.csv`;
patahan dari `reports/tables/patahan_seri.csv`; revisi dari tabel pembandingan snapshot dan
`reports/tables/revisi_snapshot.csv`. Keputusan dan alternatif yang ditolak tercatat pada
K-001–K-022 di `log-keputusan.csv`; statistik profil ada di `reports/tables/profil_seri.csv`.

## Integrasi dan rekonsiliasi

Gold rekonsiliasi berisi 30 baris untuk dua pasangan seri; 5 baris memiliki nilai dari kedua
sumber dan 25 baris tidak memiliki pasangan pada periode yang sama. Irisan memakai periode yang
benar-benar berisi nilai di kedua sumber. Kolom selisih dihitung sebagai nilai BPS dikurangi nilai
WDI; tanda positif berarti angka BPS lebih tinggi secara numerik. Angka dan satuan berikut dapat
ditarik ulang dari `data/gold/rekonsiliasi_nasional.parquet` (nilai nasional asal:
`data/gold/tabel_nasional.parquet`).

| Pasangan | Periode | Nilai BPS | Nilai WDI | Selisih numerik (BPS − WDI) | Kategori dan penjelasan |
|---|---:|---:|---:|---:|---|
| `var1410` vs `SP.REG.BRTH.ZS` | 2016 | 72,54% | 72,5% | +0,04 poin persentase | **Metode berbeda** — kedua seri mencakup anak di bawah 5 tahun, tetapi BPS menggunakan Susenas dan bukti akta; WDI menggunakan survei rumah tangga, dengan sertifikat yang dilihat pewawancara atau keterangan ibu/pengasuh. |
| `var1410` vs `SP.REG.BRTH.ZS` | 2017 | 73,18% | 77,9% | −4,72 poin persentase | **Metode berbeda** — perbedaan pengukuran yang sama berlaku; selisih ini paling besar secara numerik di antara empat periode dengan satuan persen yang sama. |
| `var1410` vs `SP.REG.BRTH.ZS` | 2018 | 71,92% | 71,9% | +0,02 poin persentase | **Metode berbeda** — cakupan umur sama, tetapi sumber survei dan cara memastikan pencatatan kelahiran tidak identik. |
| `var1410` vs `SP.REG.BRTH.ZS` | 2021 | 77,04% | 77,0% | +0,04 poin persentase | **Metode berbeda** — cakupan umur sama, tetapi sumber survei dan cara memastikan pencatatan kelahiran tidak identik. |
| `var1311` vs `VC.IHR.PSRC.P5` | 2022 | 0,03% | 0,303768746 per 100.000 penduduk | −0,273768746 (angka mentah; satuan tidak sama) | **Definisi berbeda** — BPS mengukur proporsi penduduk korban kejahatan kekerasan dalam 12 bulan, sedangkan WDI mengukur laju kematian akibat pembunuhan disengaja. Selisih aritmetis tersimpan di Gold, tetapi tidak bermakna sebagai ukuran perbedaan karena definisi dan satuannya berbeda; WDI hanya konteks. |

Kategori yang terpakai adalah **metode berbeda** dan **definisi berbeda**; keduanya menjelaskan
seluruh lima pasangan, sehingga tidak ada pasangan berangka yang diberi kategori belum
terjelaskan. Keputusan pemilihan pasangan, kategori, dan batas interpretasi tercatat di
`log-keputusan.csv` (K-028). Seri `var1831` tidak dipasangkan dengan seri WDI kelahiran karena
kelompok umurnya 0–17 tahun, bukan balita (K-003). Gold tetap menyimpan baris tanpa pasangan,
tetapi selisihnya kosong; angka selisih hanya tersedia untuk lima periode pada tabel di atas.

## Validasi dan reproduksibilitas

Jalankan `python unduh_data.py --kasus 21`, lalu `python pipeline.py`. Pipeline memeriksa
MANIFEST, menjalankan ekstraksi, membentuk Silver, profil, dan grid panel. Catatan Sprint 1
Rozak melaporkan 26 berkas cocok dan 4.261 baris mentah saat pipeline dijalankan. Uji ulang
`python -m src.common.skema data/silver/silver.parquet` pada data yang tersedia menghasilkan
**LOLOS: 2.002 baris, 8 seri, 39 wilayah, 11 berkas sumber**. Pemeriksaan ini memvalidasi kolom
wajib, kunci, tipe nilai, format periode, dan lineage manifest.

Validasi tersebut adalah pemeriksaan skema Silver, bukan validasi Pandera/Great Expectations.
Durasi pipeline dari nol tidak dicatat. Belum ada hasil benchmark Pandas vs DuckDB/Dask atau
pemrosesan arsip WDI 142 rilis di keluaran repo; keduanya tetap perlu dikerjakan/didokumentasikan.
`docs/data-dictionary.md` juga masih berupa kerangka dan perlu dilengkapi dengan tipe, rentang,
serta aturan kolom aktual.

## Pembagian kerja

Pembagian berikut mengikuti `portofolio.md`; tanggung jawab komponen dan tugas sampingan dicatat
terpisah.

| Anggota | NIM | Komponen | Tugas sampingan |
|---|---:|---|---|
| Rozak Ramdani | 124450100 | Ekstraksi dan lineage | Koordinator |
| Danil Nur Fadillah | 124450103 | Profil dan pembersihan | Penjaga Data & Evaluasi |
| Muhammad Daffa Arrafi | 124450120 | Transformasi dan panel | Integrator |
| Ahmad Bimo Akbar Arkana Putra | 124450113 | Integrasi, penyimpanan, dan skala | Analis Utama |
| Andra Ilham Bintang | 124450060 | Integrasi, penyimpanan, dan skala | Analis Utama |
| Layina Ropiqo | 124450016 | Validasi dan dokumentasi | Reproduksi & Demo |

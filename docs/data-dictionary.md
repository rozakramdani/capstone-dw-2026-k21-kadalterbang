# Data dictionary — <Kadal Terbang>

Dokumen ini menjelaskan struktur tabel Silver berdasarkan data aktual. Tipe data, satuan, rentang nilai, jumlah data kosong, dan asal setiap kolom didokumentasikan untuk mendukung pemahaman serta keterlacakan data.

## Silver Parquet dan SQL

<<<<<<< HEAD

Jumlah baris Silver Parquet: 1.988  
Jumlah kolom: 11

### Struktur Tabel SQLite

`data/silver/silver.parquet` adalah sumber muatan ke tabel SQLite `silver_observasi` dalam `data/silver/silver.sqlite3`.

DDL sumber tabel ada di `src/silver/skema_silver.sql`. Semua kolom wajib (`NOT NULL`) dan kunci primer adalah gabungan `sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw`.

| Kolom | Tipe SQLite | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | TEXT | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | Bagian kunci primer |
| seri_kode | TEXT | — | tidak | kode katalog seri | var_id dan katalog | Bagian kunci primer |
| wilayah_kode | INTEGER | kode BPS x 100 | tidak | 9999 atau 1100–9600 | pemetaan wilayah | Bagian kunci primer |
| nama_wilayah | TEXT | — | tidak | nama wilayah sumber/standar | data mentah | |
| periode | TEXT | YYYY, YYYY-Sn, YYYY-Qn, atau YYYY-MM | tidak | sesuai `jenis_periode` | tahun sumber | Bagian kunci primer |
| jenis_periode | TEXT | — | tidak | tahun, semester, triwulan, bulan | aturan format periode | |
| rincian | TEXT | label kategori | tidak | termasuk `Tidak ada` bila tanpa rincian | turvar atau default | Bagian kunci primer |
| nilai | REAL | sesuai satuan | tidak | nilai numerik | nilai sumber | |
| satuan | TEXT | — | tidak | sesuai katalog | katalog seri | |
| _berkas_raw | TEXT | jalur relatif dari data/raw | tidak | berkas pada manifest | ekstraksi | Bagian kunci primer |
| _sha256_raw | TEXT | SHA-256 heksadesimal | tidak | hash berkas sumber | manifest | Lineage |

### Struktur Silver Parquet
>>>>>>> dd155c1bf8b29b762042b01bac1aa1975c04da2c

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | str | teks | tidak | bps | Nama folder pada `_berkas_raw`; keputusan K-006 | Menunjukkan sumber penyedia data |
| seri_kode | str | kode indikator | tidak | 6 seri: var1311, var1312, var1410, var1831, var2738, var2740 | Metadata seri pada berkas mentah BPS; penyeragaman kolom K-007 | Identitas indikator |
| wilayah_kode | Int64 | kode BPS x 100 | tidak | 9999 atau kode wilayah teramati | Data wilayah BPS dan keputusan pemetaan K-001 pada `log-keputusan.csv` | Kode numerik wilayah pengamatan |
| nama_wilayah | str | teks | tidak | 39 nama wilayah teramati | Data wilayah BPS dan keputusan pemetaan K-001 pada `log-keputusan.csv` | Nama provinsi atau Indonesia |
| periode | str | tahun | tidak | 12 periode teramati | Kolom tahun pada data mentah; keputusan K-009 pada `log-keputusan.csv` | Tahun pengamatan |
| jenis_periode | str | teks | tidak | tahun | Data sumber BPS | Jenis periode pengamatan |
| rincian | str | teks | tidak | Tidak ada | Data sumber BPS | Keterangan tambahan indikator |
| nilai | float64 | Persen | tidak | 0–100 | Data sumber BPS | Nilai indikator |
| satuan | str | teks | tidak | Persen | Data sumber BPS | Satuan pengukuran nilai |
| _berkas_raw | str | path berkas | tidak | 10 berkas sumber teramati | Lokasi berkas pada `data/raw` dan `data/raw/MANIFEST.csv`; keputusan penyeragaman kolom K-007 | Menyimpan lokasi berkas mentah asal data |
| _sha256_raw | str | SHA-256 | tidak | 6 hash unik teramati | Hash berkas mentah pada `data/raw/MANIFEST.csv` | Identitas integritas berkas sumber |

## Contoh Penelusuran Data (Data Lineage)

Setiap baris Silver dapat ditelusuri ke berkas mentah menggunakan kolom `_berkas_raw` dan `_sha256_raw`.

Contoh satu baris dari `data/silver/silver.parquet`:

| Kolom | Nilai |
|---|---|
| sumber | bps |
| seri_kode | var1311 |
| wilayah_kode | 9400 |
| nama_wilayah | PAPUA |
| periode | 2015 |
| jenis_periode | tahun |
| rincian | Tidak ada |
| nilai | 0.16 |
| satuan | Persen |
| _berkas_raw | bps/2026-10-17/json/sdg16_16_1_3_a_v1311.json |
| _sha256_raw | ce796563d5698b7aed791c6fbeb7e0f9610e8077c1bd8bd4fa55e3d2169337a1 |

### Cara penelusuran

1. Kolom `_berkas_raw` menunjukkan lokasi berkas mentah yang menjadi sumber baris Silver.
2. Berkas tersebut dapat dicari pada direktori `data/raw` menggunakan path yang tercantum.
3. Kolom `_sha256_raw` menyimpan hash SHA-256 berkas mentah.
4. Hash dapat dicocokkan dengan catatan pada `MANIFEST.csv` untuk membantu memeriksa integritas berkas sumber.

Dengan demikian, asal data pada setiap baris Silver dapat ditelusuri melalui lokasi berkas mentah dan identitas hash-nya.

**Catatan verifikasi contoh:**

Hash `ce796563d5698b7aed791c6fbeb7e0f9610e8077c1bd8bd4fa55e3d2169337a1` ditemukan pada `data/raw/MANIFEST.csv` untuk dua berkas snapshot, yaitu:

- `bps/2026-10-17/json/sdg16_16_1_3_a_v1311.json`
- `bps/2026-10-20/json/sdg16_16_1_3_a_v1311.json`

Keduanya memiliki ukuran 21.885 byte dan hash yang sama. Contoh baris Silver menggunakan path snapshot tanggal 17 Oktober 2026. Oleh karena itu, pencocokan hash perlu dilakukan bersama `_berkas_raw`, bukan menggunakan hash saja, untuk menentukan berkas snapshot yang dimaksud.
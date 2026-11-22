# Data dictionary — <Kadal Terbang>

Dokumen ini menjelaskan struktur tabel Silver berdasarkan data aktual. Tipe data, satuan, rentang nilai, jumlah data kosong, dan asal setiap kolom didokumentasikan untuk mendukung pemahaman serta keterlacakan data.

## data/silver/silver.parquet

Jumlah baris: 1.988  
Jumlah kolom: 11

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
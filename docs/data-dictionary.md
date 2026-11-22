# Data dictionary — <Nama tim>

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## Silver Parquet dan SQL

`data/silver/silver.parquet` adalah sumber muatan ke tabel SQLite `silver_observasi`
dalam `data/silver/silver.sqlite3`. DDL sumber tabel ada di
`src/silver/skema_silver.sql`; semua kolom wajib (`NOT NULL`) dan kunci primer adalah
gabungan `sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw`.

| Kolom | Tipe SQLite | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | TEXT | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | Bagian kunci primer |
| seri_kode | TEXT | — | tidak | kode katalog seri | var_id dan katalog | Bagian kunci primer |
| wilayah_kode | INTEGER | kode BPS x 100 | tidak | 9999 atau 1100–9600 | pemetaan wilayah | Bagian kunci primer |
| nama_wilayah | TEXT | — | tidak | nama wilayah sumber/standar | data mentah | |
| periode | TEXT | YYYY, YYYY-Sn, YYYY-Qn, atau YYYY-MM | tidak | sesuai `jenis_periode` | tahun sumber | Bagian kunci primer |
| jenis_periode | TEXT | tahun, semester, triwulan, bulan | tidak | salah satu nilai tersebut | aturan format periode | |
| rincian | TEXT | label kategori | tidak | termasuk `Tidak ada` bila tanpa rincian | turvar atau default | Bagian kunci primer |
| nilai | REAL | sesuai satuan | tidak | nilai numerik | nilai sumber | |
| satuan | TEXT | mis. persen | tidak | sesuai katalog | katalog seri | |
| _berkas_raw | TEXT | jalur relatif dari data/raw | tidak | berkas pada manifest | ekstraksi | Bagian kunci primer |
| _sha256_raw | TEXT | SHA-256 heksadesimal | tidak | hash berkas sumber | manifest | Lineage |

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

# Data dictionary — <Nama tim>

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | |
| wilayah_kode | int | kode BPS x 100 | tidak | 9999 atau 1100–9600 | log K-… | |

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

## data/gold/tabel_nasional.parquet

Satu baris per periode-seri untuk `var1311`, `var1312`, `var2738`, `var2740`,
`var1410`, `var1831`, `VC.IHR.PSRC.P5`, dan `SP.REG.BRTH.ZS`. Snapshot terbaru
dipilih per seri. Angka nasional BPS/WDI berasal dari baris `wilayah_kode=9999`;
periode BPS tanpa baris Indonesia disimpan dengan `nilai` kosong dan penjelasan
di `asal_nilai`. Tidak dilakukan rata-rata provinsi karena penyebut/bobot populasi
atau kelompok sasaran yang diperlukan tidak tersedia pada Silver.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| periode | string | tahun | tidak | `YYYY` | Silver, snapshot terbaru | Periode tahunan sumber |
| seri_kode | string | kode indikator | tidak | enam seri utama dan dua pembanding | Silver | Satu seri per baris |
| sumber | string | — | tidak | `bps` atau `wdi` | Silver | Asal penerbit data |
| wilayah_kode | int | kode wilayah | tidak | `9999` | Aturan tabel nasional | Menandai cakupan Indonesia, termasuk saat nilai nasional tidak terbit |
| nama_wilayah | string | — | tidak | `Indonesia` | Aturan tabel nasional | |
| rincian | string | — | tidak | `Tidak ada` atau `total` | Silver | Rincian terpilih untuk seri |
| nilai | float | satuan per seri | ya | nilai numerik Silver atau kosong jika tidak ada baris Indonesia | Baris Indonesia Silver | Tidak dihitung ulang |
| satuan | string | katalog indikator | tidak | `persen` atau `per 100.000 penduduk` | Silver | |
| asal_nilai | string | keterangan provenance | tidak | baris langsung atau tidak ada padanan nasional | Aturan pemilihan Gold | Menjelaskan apakah nilai diterbitkan langsung atau tidak tersedia; alasan tidak melakukan agregasi tercantum di sini |
| _berkas_raw | string | path relatif | tidak | path Bronze; beberapa path dipisahkan `;` | Silver | Berkas mentah yang mendukung baris |
| _sha256_raw | string | SHA-256 | tidak | hash Bronze; beberapa hash dipisahkan `;` dengan urutan yang sama | Silver | Hash untuk pemeriksaan lineage |

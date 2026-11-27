# Laporan Validasi Silver dan Gold

- Jumlah baris Silver: 2002
- Jumlah seri Silver: 8
- Jumlah aturan: 10
- Aturan lolos: 10

## Hasil Pemeriksaan

- Kelengkapan skema Silver: **LOLOS** — Seluruh kolom wajib tersedia dan tidak memiliki nilai kosong.
- Rentang nilai persen: **LOLOS** — Nilai dengan satuan persen harus berada pada rentang 0–100.
- Keunikan kunci Silver: **LOLOS** — Tidak ditemukan duplikasi berdasarkan kunci Silver.
- Konsistensi satuan: **LOLOS** — Setiap seri menggunakan satuan yang konsisten.
- Keunikan kunci Gold setelah snapshot: **LOLOS** — Setiap kombinasi seri, wilayah, periode, dan rincian hanya muncul satu kali.
- Pemisahan seri pencatatan kelahiran: **LOLOS** — var1410 dan var1831 tetap tercatat sebagai dua seri berbeda.
- Keunikan kunci panel Gold: **LOLOS** — Setiap kombinasi wilayah, periode, dan seri hanya muncul satu kali.
- Konsistensi satuan indikator Gold: **LOLOS** — Setiap indikator Gold menggunakan satu satuan yang tidak kosong.
- Kelengkapan pasangan Gold dan Silver: **LOLOS** — Setiap periode sumber pada sel Gold tersedia ditemukan di Silver.
- Kategori rekonsiliasi berpasangan: **LOLOS** — Setiap baris rekonsiliasi berpasangan memiliki kategori penjelasan yang valid.
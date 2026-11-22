# Hasil Validasi Silver

Tanggal pemeriksaan: 2026-11-22  
Berkas: `data/silver/silver.parquet`

## Validasi skema

Perintah:

```powershell
python -m src.common.skema data/silver/silver.parquet
```

Keluaran:

```text
LOLOS  2,002 baris, 8 seri, 39 wilayah, 11 berkas sumber
```

## Keunikan kunci

Kunci baku dari `src.common.skema.KUNCI`:

```text
sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw
```

Keluaran pemeriksaan:

```text
Jumlah baris: 2002
Jumlah baris dengan kunci duplikat: 0
Jumlah kunci unik: 2002
Hasil: LOLOS
```

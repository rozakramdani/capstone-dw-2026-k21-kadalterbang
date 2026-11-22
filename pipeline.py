"""Jalankan ekstraksi, pembentukan Silver, dan grid panel provinsi.

    python unduh_data.py --kasus <N>     # sekali, isi data/raw/
    python pipeline.py

Keluaran: Silver ber-lineage snapshot, profil semua snapshot, dan grid panel snapshot terbaru.
"""
import sys

import pandas as pd
from src.validasi import jalankan as jalankan_validasi
from src import ekstraksi
from src.common.manifest import baca, periksa
from src.gold.grid_provinsi import bentuk_grid
from src.profiling.profil_anomali import jalankan_profiling
from src.silver.buat_silver import buat_silver


def main():
    jumlah, salah = periksa()
    if salah:
        sys.exit(
            f"data/raw tidak cocok dengan MANIFEST.csv ({len(salah)} berkas): "
            f"{salah[:5]}. Jalankan ulang unduh_data.py."
        )
    print(f"data/raw: {jumlah} berkas cocok dengan MANIFEST.csv")

    mentah = ekstraksi.jalankan()
    terdaftar = set(baca())
    terproses = set(mentah)
    if terproses != terdaftar:
        belum_dibaca = sorted(terdaftar - terproses)
        tidak_terdaftar = sorted(terproses - terdaftar)
        sys.exit(
            f"Berkas ekstraksi tidak cocok dengan MANIFEST.csv; "
            f"belum dibaca={belum_dibaca}, tidak terdaftar={tidak_terdaftar}"
        )

    baris = sum(len(tabel) for tabel in mentah.values())
    print(f"ekstraksi selesai: {len(mentah)} berkas, {baris} baris mentah")

    buat_silver()
    jalankan_profiling()
    grid, indonesia, matriks = bentuk_grid()
    print(
        f"grid provinsi: {len(grid)} sel; Indonesia terpisah: {len(indonesia)} baris; "
        f"sel kosong pada tahun terbit: {int(matriks['sel_kosong'].sum())}"
    )

    silver = pd.read_parquet("data/silver/silver.parquet")
    hasil_validasi = jalankan_validasi(silver, grid)
    print(f"Hasil validasi: {hasil_validasi}")

if __name__ == "__main__":
    main()

"""Jalankan ekstraksi, pembentukan Silver, dan panel Gold provinsi.

    python unduh_data.py --kasus <N>     # sekali, isi data/raw/
    python pipeline.py

Keluaran: Silver ber-lineage snapshot, profil semua snapshot, panel Gold, matriks
ketersediaan, dan rekonsiliasi nasional.
"""
import sys
import pandas as pd

from src.validasi import jalankan as jalankan_validasi
from src import ekstraksi
from src.common.manifest import baca, periksa
from src.gold.panel_provinsi import bentuk_panel_provinsi
from src.gold.rekonsiliasi import bentuk_tabel_rekonsiliasi
from src.gold.tabel_nasional import bentuk_tabel_nasional
from src.gold.muat_sql import muat as muat_sql
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
    grid, indonesia, matriks, ringkasan = bentuk_panel_provinsi()
    nasional = bentuk_tabel_nasional()
    rekonsiliasi = bentuk_tabel_rekonsiliasi(nasional)
    silver = pd.read_parquet("data/silver/silver.parquet")

    hasil_validasi = jalankan_validasi(
        silver,
        grid,
        rekonsiliasi,
    )

    jumlah_sql = muat_sql()
    print(
        f"panel Gold: {len(grid)} baris ({int(grid['tersedia'].sum())} terisi); "
        f"Indonesia terpisah: {len(indonesia)} baris; "
        f"sel kosong pada tahun terbit: {int(matriks['sel_kosong'].sum())}; "
        f"observasi Gold: {ringkasan['baris_gold_observasi']}; "
        f"tabel nasional: {len(nasional)} baris "
        f"({int(nasional['nilai'].notna().sum())} nilai nasional terbit); "
        f"rekonsiliasi: {len(rekonsiliasi)} baris "
        f"({int(rekonsiliasi['berpasangan'].sum())} periode berpasangan)"
    )
    print(
        "SQLite: "
        + ", ".join(f"{tabel}={jumlah:,}" for tabel, jumlah in jumlah_sql.items())
    )

if __name__ == "__main__":
    main()

"""Jalankan ekstraksi, pembentukan Silver, dan panel Gold provinsi.

    python unduh_data.py --kasus <N>     # sekali, isi data/raw/
    python pipeline.py

Keluaran: Silver ber-lineage snapshot, profil semua snapshot, panel Gold, dan matriks ketersediaan.
"""
import sys

from src import ekstraksi
from src.common.manifest import baca, periksa
from src.gold.panel_provinsi import bentuk_panel_provinsi
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
    print(
        f"panel Gold: {len(grid)} baris ({int(grid['tersedia'].sum())} terisi); "
        f"Indonesia terpisah: {len(indonesia)} baris; "
        f"sel kosong pada tahun terbit: {int(matriks['sel_kosong'].sum())}; "
        f"observasi Gold: {ringkasan['baris_gold_observasi']}"
    )

if __name__ == "__main__":
    main()

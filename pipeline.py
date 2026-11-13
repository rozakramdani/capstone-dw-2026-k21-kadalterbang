"""Jalankan Tahap 1: verifikasi data mentah dan ekstraksi ke tabel panjang.

    python unduh_data.py --kasus <N>     # sekali, isi data/raw/
    python pipeline.py

Tahap Silver, Gold, dan validasi belum dijalankan karena implementasinya belum tersedia.
"""
import sys

from src import ekstraksi
from src.common.manifest import baca, periksa


hasil = {}


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

    hasil["ekstraksi"] = mentah
    baris = sum(len(tabel) for tabel in mentah.values())
    print(f"ekstraksi selesai: {len(mentah)} berkas, {baris} baris mentah")
    print("Tahap Silver, Gold, dan validasi belum dijalankan.")


if __name__ == "__main__":
    main()

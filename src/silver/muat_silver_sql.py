"""Muat data/silver/silver.parquet ke tabel SQLite silver_observasi."""
import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from src.common.skema import KOLOM, periksa_silver

ROOT = Path(__file__).resolve().parents[2]
DDL = Path(__file__).with_name("skema_silver.sql")


def muat(input_path, database_path):
    """Ganti isi tabel secara atomik setelah memvalidasi Silver."""
    data = pd.read_parquet(input_path)
    kesalahan = periksa_silver(data)
    if kesalahan:
        raise ValueError("Data Silver tidak lolos skema: " + "; ".join(kesalahan))

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as koneksi:
        koneksi.executescript(DDL.read_text(encoding="utf-8"))
        with koneksi:
            koneksi.execute("DELETE FROM silver_observasi")
            kolom = ", ".join(f'"{nama}"' for nama in KOLOM)
            parameter = ", ".join("?" for _ in KOLOM)
            pernyataan = (
                f"INSERT INTO silver_observasi ({kolom}) "
                f"VALUES ({parameter})"
            )
            baris = (
                tuple(nilai.item() if hasattr(nilai, "item") else nilai for nilai in rekaman)
                for rekaman in data[KOLOM].itertuples(index=False, name=None)
            )
            koneksi.executemany(pernyataan, baris)
            jumlah = koneksi.execute(
                "SELECT COUNT(*) FROM silver_observasi"
            ).fetchone()[0]
            if jumlah != len(data):
                raise RuntimeError(
                    f"Jumlah baris SQLite tidak cocok: {jumlah} != {len(data)}"
                )

    return jumlah


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "silver" / "silver.parquet",
        help="Parquet Silver yang akan dimuat",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=ROOT / "data" / "silver" / "silver.sqlite3",
        help="Berkas basis data SQLite keluaran",
    )
    args = parser.parse_args()
    jumlah = muat(args.input, args.database)
    print(f"Berhasil memuat {jumlah:,} baris ke {args.database}")


if __name__ == "__main__":
    main()

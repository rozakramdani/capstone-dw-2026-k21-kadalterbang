"""Muat Silver, Gold, dan tabel rekonsiliasi ke basis data SQLite."""
import sqlite3
from pathlib import Path

import pandas as pd

from src.common.skema import KOLOM, periksa_silver


ROOT = Path(__file__).resolve().parents[2]
DDL = Path(__file__).with_name("skema_sql.sql")
DATABASE = ROOT / "data" / "gold" / "warehouse.sqlite3"

TABEL = {
    "silver_observasi": (
        ROOT / "data" / "silver" / "silver.parquet",
        KOLOM,
        ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"],
        False,
    ),
    "panel_provinsi": (
        ROOT / "data" / "gold" / "panel_provinsi.parquet",
        [
            "seri_kode", "wilayah_kode", "periode", "nama_wilayah", "rincian",
            "nilai", "satuan", "snapshot", "periode_sumber",
            "jumlah_periode_sumber", "_berkas_raw", "_sha256_raw",
            "kategori_anomali", "flag_kandidat_anomali", "flag_outlier",
            "flag_galat_input", "flag_patahan_seri", "tersedia",
        ],
        ["wilayah_kode", "periode", "seri_kode"],
        False,
    ),
    "tabel_nasional": (
        ROOT / "data" / "gold" / "tabel_nasional.parquet",
        [
            "periode", "seri_kode", "sumber", "wilayah_kode", "nama_wilayah",
            "rincian", "nilai", "satuan", "asal_nilai", "_berkas_raw",
            "_sha256_raw",
        ],
        ["periode", "seri_kode"],
        False,
    ),
    "rekonsiliasi_nasional": (
        ROOT / "reports" / "tables" / "rekonsiliasi_nasional.csv",
        [
            "periode", "seri_kode", "sumber", "nama_seri", "nilai", "satuan",
            "rincian", "wilayah_kode", "nama_wilayah", "_berkas_raw",
            "_sha256_raw",
        ],
        ["periode", "seri_kode"],
        True,
    ),
}


def _baca_frame(path, csv):
    if csv:
        return pd.read_csv(path)
    return pd.read_parquet(path)


def _nilai_sql(nilai):
    if pd.isna(nilai):
        return None
    if hasattr(nilai, "item"):
        nilai = nilai.item()
    if isinstance(nilai, bool):
        return int(nilai)
    return nilai


def muat(database_path=DATABASE):
    """Ganti seluruh isi tabel secara atomik dan verifikasi hitungan baris."""
    frames = {}
    for tabel, (path, kolom, kunci, csv) in TABEL.items():
        data = _baca_frame(path, csv)
        kurang = set(kolom) - set(data.columns)
        if kurang:
            raise ValueError(f"Kolom {tabel} tidak lengkap: {sorted(kurang)}")
        if data.duplicated(kunci).any():
            raise ValueError(f"{tabel} memiliki kunci duplikat: {kunci}")
        if tabel == "silver_observasi":
            kesalahan = periksa_silver(data)
            if kesalahan:
                raise ValueError("Data Silver tidak lolos skema: " + "; ".join(kesalahan))
        if tabel == "panel_provinsi" and not data["tersedia"].equals(data["nilai"].notna()):
            raise ValueError("Flag ketersediaan panel tidak sesuai dengan nilai.")
        frames[tabel] = data[kolom]

    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as koneksi:
        koneksi.executescript(DDL.read_text(encoding="utf-8"))
        with koneksi:
            for tabel, data in frames.items():
                kolom = list(data.columns)
                nama_kolom = ", ".join(f'"{nama}"' for nama in kolom)
                placeholder = ", ".join("?" for _ in kolom)
                koneksi.execute(f'DELETE FROM "{tabel}"')
                koneksi.executemany(
                    f'INSERT INTO "{tabel}" ({nama_kolom}) VALUES ({placeholder})',
                    (
                        tuple(_nilai_sql(nilai) for nilai in baris)
                        for baris in data.itertuples(index=False, name=None)
                    ),
                )
                jumlah = koneksi.execute(
                    f'SELECT COUNT(*) FROM "{tabel}"'
                ).fetchone()[0]
                if jumlah != len(data):
                    raise RuntimeError(
                        f"Jumlah baris SQLite {tabel} tidak cocok: {jumlah} != {len(data)}"
                    )

    return {tabel: len(data) for tabel, data in frames.items()}

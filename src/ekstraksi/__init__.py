"""Pembaca data mentah BPS untuk Tahap 1 (Ekstraksi).

Berkas dibaca tanpa pembersihan nilai. Setiap DataFrame diberi jalur relatif dan
sha256 sumbernya agar hasil tahap berikutnya tetap dapat ditelusuri.
"""
import csv
import io
import json
import re
from itertools import product
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

_VAR_IDS = ("1311", "1312", "2738", "2740", "1410", "1831")
_BERKAS_SERI = re.compile(r"(?:^|_)v(?:" + "|".join(_VAR_IDS) + r")$")
_KOLOM_JSON = (
    "var_id", "wilayah_id", "wilayah", "turvar_id", "turvar",
    "tahun_id", "tahun", "periode_id", "periode", "nilai", "satuan",
)


def _decode(path):
    """Dekode teks tanpa mengganti karakter yang tidak dikenal."""
    data = path.read_bytes()
    kesalahan = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as error:
            kesalahan.append(error)
    raise kesalahan[-1]


def _baca_csv(path):
    teks = _decode(path)
    contoh = "\n".join(teks.splitlines()[:10])
    try:
        pemisah = csv.Sniffer().sniff(contoh, delimiters=",;\t|").delimiter
    except csv.Error:
        pemisah = max((",", ";", "\t", "|"), key=contoh.count)

    pembaca = csv.DictReader(io.StringIO(teks), delimiter=pemisah)
    pola_desimal_koma = re.compile(r"^[+-]?\d+,\d+$")
    nilai = [row.get("nilai", "").strip() for _, row in zip(range(100), pembaca)]
    desimal = "," if any(pola_desimal_koma.fullmatch(v) for v in nilai) else "."
    return pd.read_csv(
        io.StringIO(teks),
        sep=pemisah,
        decimal=desimal,
        keep_default_na=False,
    )


def _nilai_dimension(item, nama, konteks):
    if not isinstance(item, dict) or "val" not in item or "label" not in item:
        raise ValueError(f"Dimensi {nama} tidak valid pada {konteks}: {item!r}")
    return item


def _baca_json(path):
    isi = json.loads(_decode(path))
    objek = isi if isinstance(isi, list) else [isi]
    baris = []

    for indeks, data in enumerate(objek):
        konteks = f"{path} objek ke-{indeks}"
        if not isinstance(data, dict) or not isinstance(data.get("datacontent"), dict):
            raise ValueError(f"Struktur BPS tidak memiliki datacontent berbentuk objek: {konteks}")
        dimensi = {}
        for nama in ("vervar", "var", "turvar", "tahun", "turtahun"):
            nilai = data.get(nama)
            if not isinstance(nilai, list):
                raise ValueError(f"Dimensi {nama} tidak berbentuk daftar: {konteks}")
            dimensi[nama] = [_nilai_dimension(item, nama, konteks) for item in nilai]

        indeks_kunci = {}
        for kombinasi in product(
            dimensi["vervar"], dimensi["var"], dimensi["turvar"],
            dimensi["tahun"], dimensi["turtahun"],
        ):
            kunci = "".join(str(d["val"]) for d in kombinasi)
            if kunci in indeks_kunci:
                raise ValueError(f"Kunci datacontent ambigu {kunci!r}: {konteks}")
            indeks_kunci[kunci] = kombinasi

        for kunci, nilai in data["datacontent"].items():
            if kunci not in indeks_kunci:
                raise ValueError(f"Kunci datacontent tidak cocok dengan dimensi {kunci!r}: {konteks}")
            vervar, var, turvar, tahun, turtahun = indeks_kunci[kunci]
            baris.append({
                "var_id": var["val"],
                "wilayah_id": vervar["val"],
                "wilayah": vervar["label"],
                "turvar_id": turvar["val"],
                "turvar": turvar["label"],
                "tahun_id": tahun["val"],
                "tahun": tahun["label"],
                "periode_id": turtahun["val"],
                "periode": turtahun["label"],
                "nilai": nilai,
                "satuan": var.get("unit", ""),
            })

    return pd.DataFrame.from_records(baris, columns=_KOLOM_JSON)


def jalankan(raw=RAW):
    """Kembalikan {jalur relatif data/raw: DataFrame BPS mentah}."""
    raw = Path(raw)
    akar_bps = raw / "bps"
    berkas = [
        path for path in akar_bps.rglob("*")
        if path.is_file()
        and (path.suffix.lower() == ".csv" or (
            path.suffix.lower() == ".json" and path.parent.name == "json"
        ))
        and _BERKAS_SERI.search(path.stem)
    ]
    berkas.sort(key=lambda path: path.relative_to(raw).as_posix())
    if not berkas:
        raise FileNotFoundError(f"Tidak ada berkas seri BPS yang didukung di {akar_bps}")

    hasil = {}
    for path in berkas:
        relatif = path.relative_to(raw).as_posix()
        tabel = _baca_csv(path) if path.suffix.lower() == ".csv" else _baca_json(path)
        tabel["_berkas_raw"] = relatif
        tabel["_sha256_raw"] = sha256_raw(relatif, raw=raw)
        hasil[relatif] = tabel
    return hasil

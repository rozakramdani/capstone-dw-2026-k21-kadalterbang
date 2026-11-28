"""Bangun tabel Gold nasional untuk seri utama dan pembanding."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver" / "silver.parquet"
GOLD = ROOT / "data" / "gold"
KODE_INDONESIA = "9999"
SERI_UTAMA = ("var1311", "var1312", "var2738", "var2740", "var1410", "var1831")
SERI_PEMBANDING = ("VC.IHR.PSRC.P5", "SP.REG.BRTH.ZS")
SERI_NASIONAL = SERI_UTAMA + SERI_PEMBANDING
RINCIAN = {seri: "Tidak ada" for seri in SERI_UTAMA}
RINCIAN.update({seri: "total" for seri in SERI_PEMBANDING})
ASAL_LANGSUNG = {
    **{
        seri: (
            "Baris Indonesia BPS (wilayah_kode=9999); nilai nasional diterbitkan "
            "langsung, bukan agregasi provinsi."
        )
        for seri in SERI_UTAMA
    },
    **{
        seri: (
            "Baris Indonesia WDI (wilayah_kode=9999); seri pembanding diterbitkan "
            "langsung, bukan agregasi provinsi."
        )
        for seri in SERI_PEMBANDING
    },
}
ASAL_TANPA_NASIONAL = (
    "Tidak ada padanan nasional terbitan untuk periode ini. Tidak diagregasi dari "
    "provinsi karena proporsi memerlukan bobot/penyebut populasi, rumah tangga, "
    "anak, atau korban yang sesuai; penyebut tersebut tidak tersedia di Silver."
)


def _baca_silver(path):
    data = pd.read_parquet(path)
    wajib = {
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode",
        "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw",
    }
    hilang = wajib - set(data.columns)
    if hilang:
        raise ValueError(f"Kolom Silver tidak lengkap: {sorted(hilang)}")
    data = data[data["seri_kode"].isin(SERI_NASIONAL)].copy()
    seri_ada = set(data["seri_kode"])
    if seri_ada != set(SERI_NASIONAL):
        raise ValueError(f"Seri nasional Silver tidak cocok: {sorted(seri_ada)}")

    data["wilayah_kode"] = (
        data["wilayah_kode"].astype(str).str.replace(r"\.0$", "", regex=True)
    )
    for kolom in ("periode", "jenis_periode", "rincian"):
        data[kolom] = data[kolom].astype(str).str.strip()
    data["jenis_periode"] = data["jenis_periode"].str.lower()
    data["nilai"] = pd.to_numeric(data["nilai"], errors="raise")
    data["_snapshot"] = data["_berkas_raw"].astype(str).str.extract(
        r"(\d{4}-\d{2}-\d{2})"
    )
    if data["_snapshot"].isna().any():
        raise ValueError("Tanggal snapshot tidak dapat ditentukan dari _berkas_raw.")
    if data[["_berkas_raw", "_sha256_raw"]].isna().any().any():
        raise ValueError("Baris Silver tanpa lineage berkas atau SHA-256.")
    return data


def _lineage(baris):
    pasangan = baris[["_berkas_raw", "_sha256_raw"]].drop_duplicates()
    berkas = pasangan["_berkas_raw"].astype(str).tolist()
    hashes = pasangan["_sha256_raw"].astype(str).tolist()
    if not berkas or not hashes or any(not nilai for nilai in berkas + hashes):
        raise ValueError("Baris Gold nasional memiliki lineage kosong.")
    return ";".join(berkas), ";".join(hashes)


def bentuk_tabel_nasional(silver=SILVER, gold=GOLD):
    """Simpan satu baris per periode-seri yang terbit pada snapshot terpilih."""
    data = _baca_silver(silver)
    snapshot_terbaru = data.groupby("seri_kode")["_snapshot"].max()
    terbaru = data[
        data["_snapshot"] == data["seri_kode"].map(snapshot_terbaru)
    ].copy()
    tahunan = terbaru[
        (terbaru["jenis_periode"] == "tahun")
        & (terbaru["rincian"] == terbaru["seri_kode"].map(RINCIAN))
    ].copy()
    if tahunan.empty:
        raise ValueError("Tidak ada observasi tahunan untuk seri nasional.")
    if set(tahunan["seri_kode"]) != set(SERI_NASIONAL):
        raise ValueError("Setiap seri nasional harus memiliki observasi tahunan terpilih.")

    kunci = ["seri_kode", "wilayah_kode", "periode"]
    if tahunan.duplicated(kunci).any():
        raise ValueError(f"Silver terpilih memiliki kunci nasional ambigu: {kunci}")

    hasil = []
    for (seri, periode), grup in tahunan.groupby(["seri_kode", "periode"], sort=True):
        indonesia = grup[grup["wilayah_kode"] == KODE_INDONESIA]
        if len(indonesia) > 1:
            raise ValueError(f"Baris Indonesia ganda untuk {seri} pada {periode}.")
        if not indonesia.empty:
            terpilih = indonesia.iloc[0]
            berkas, sha256 = _lineage(indonesia)
            hasil.append(
                {
                    "periode": periode,
                    "seri_kode": seri,
                    "sumber": terpilih["sumber"],
                    "wilayah_kode": 9999,
                    "nama_wilayah": "Indonesia",
                    "rincian": terpilih["rincian"],
                    "nilai": terpilih["nilai"],
                    "satuan": terpilih["satuan"],
                    "asal_nilai": ASAL_LANGSUNG[seri],
                    "_berkas_raw": berkas,
                    "_sha256_raw": sha256,
                }
            )
        elif seri in SERI_UTAMA:
            berkas, sha256 = _lineage(grup)
            hasil.append(
                {
                    "periode": periode,
                    "seri_kode": seri,
                    "sumber": grup["sumber"].iloc[0],
                    "wilayah_kode": 9999,
                    "nama_wilayah": "Indonesia",
                    "rincian": grup["rincian"].iloc[0],
                    "nilai": float("nan"),
                    "satuan": grup["satuan"].iloc[0],
                    "asal_nilai": ASAL_TANPA_NASIONAL,
                    "_berkas_raw": berkas,
                    "_sha256_raw": sha256,
                }
            )

    tabel = pd.DataFrame(hasil).sort_values(
        ["periode", "seri_kode"], kind="stable"
    ).reset_index(drop=True)
    kunci_nasional = ["periode", "seri_kode"]
    if tabel.duplicated(kunci_nasional).any():
        raise ValueError(f"Tabel nasional memiliki kunci duplikat: {kunci_nasional}")
    if tabel[["_berkas_raw", "_sha256_raw", "asal_nilai"]].isna().any().any():
        raise ValueError("Tabel nasional memiliki kolom asal atau lineage kosong.")
    if tabel[["_berkas_raw", "_sha256_raw", "asal_nilai"]].astype(str).eq("").any().any():
        raise ValueError("Tabel nasional memiliki kolom asal atau lineage kosong.")

    gold = Path(gold)
    gold.mkdir(parents=True, exist_ok=True)
    tabel.to_parquet(gold / "tabel_nasional.parquet", index=False)
    return tabel


if __name__ == "__main__":
    tabela = bentuk_tabel_nasional()
    print(f"Tabel nasional: {len(tabela)} baris; {tabela['nilai'].notna().sum()} nilai terbit")

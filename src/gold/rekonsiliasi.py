"""Rekonsiliasi pasangan seri nasional tanpa menyamakan perbedaan sumber."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "gold"

PASANGAN = (
    {
        "seri_utama": "var1410",
        "seri_pembanding": "SP.REG.BRTH.ZS",
        "kategori_penjelasan": "metode berbeda",
        "catatan": (
            "Kedua sumber mencakup anak di bawah 5 tahun. BPS menggunakan Susenas "
            "dan definisi kelahiran tercatat yang dibuktikan dengan akta; WDI "
            "menggunakan survei rumah tangga, dengan bukti sertifikat dilihat "
            "pewawancara atau keterangan ibu/pengasuh."
        ),
    },
    {
        "seri_utama": "var1311",
        "seri_pembanding": "VC.IHR.PSRC.P5",
        "kategori_penjelasan": "definisi berbeda",
        "catatan": (
            "BPS mengukur persentase penduduk yang menjadi korban kejahatan "
            "kekerasan dalam 12 bulan; WDI mengukur kematian akibat pembunuhan "
            "disengaja per 100.000 penduduk. Nilai WDI hanya menjadi konteks."
        ),
    },
)
KATEGORI = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
}


def _pilih_seri(tabel_nasional, seri, nama):
    kolom = [
        "periode",
        "nilai",
        "satuan",
        "_berkas_raw",
        "_sha256_raw",
    ]
    data = tabel_nasional.loc[tabel_nasional["seri_kode"].eq(seri), kolom].copy()
    if data.empty:
        raise ValueError(f"Tidak ada seri {seri} pada tabel nasional.")
    if data["periode"].isna().any() or data["periode"].duplicated().any():
        raise ValueError(f"Periode seri {seri} kosong atau duplikat.")
    data["periode"] = data["periode"].astype(str).str.strip()
    data["nilai"] = pd.to_numeric(data["nilai"], errors="raise")
    return data.rename(
        columns={
            "nilai": f"nilai_{nama}",
            "satuan": f"satuan_{nama}",
            "_berkas_raw": f"_berkas_raw_{nama}",
            "_sha256_raw": f"_sha256_raw_{nama}",
        }
    )


def bentuk_tabel_rekonsiliasi(tabel_nasional, gold=GOLD):
    """Simpan rekonsiliasi outer-join; periode tanpa pasangan tetap dipertahankan."""
    hasil_pasangan = []
    for pasangan in PASANGAN:
        utama = _pilih_seri(
            tabel_nasional, pasangan["seri_utama"], "utama"
        )
        pembanding = _pilih_seri(
            tabel_nasional, pasangan["seri_pembanding"], "pembanding"
        )
        hasil = utama.merge(
            pembanding,
            on="periode",
            how="outer",
            validate="one_to_one",
            sort=True,
        )
        hasil["seri_utama"] = pasangan["seri_utama"]
        hasil["seri_pembanding"] = pasangan["seri_pembanding"]
        hasil["berpasangan"] = (
            hasil["nilai_utama"].notna() & hasil["nilai_pembanding"].notna()
        )
        hasil["selisih"] = (
            hasil["nilai_utama"] - hasil["nilai_pembanding"]
        ).where(hasil["berpasangan"])
        hasil["kategori_penjelasan"] = pasangan["kategori_penjelasan"]
        hasil.loc[~hasil["berpasangan"], "kategori_penjelasan"] = pd.NA
        hasil["catatan"] = pasangan["catatan"]
        hasil["dugaan"] = pd.NA
        hasil["bukti_dicari"] = pd.NA
        belum_terjelaskan = hasil["kategori_penjelasan"].eq("belum terjelaskan")
        if (
            hasil.loc[belum_terjelaskan, ["dugaan", "bukti_dicari"]]
            .isna()
            .any()
            .any()
        ):
            raise ValueError(
                "Pasangan belum terjelaskan harus menyertakan dugaan dan bukti yang dicari."
            )
        hasil_pasangan.append(hasil)

    tabel = pd.concat(hasil_pasangan, ignore_index=True)
    if not tabel["kategori_penjelasan"].dropna().isin(KATEGORI).all():
        raise ValueError("Kategori penjelasan rekonsiliasi tidak dikenal.")
    tabel = tabel.sort_values(
        ["seri_utama", "periode"], kind="stable"
    ).reset_index(drop=True)
    kolom = [
        "periode",
        "seri_utama",
        "seri_pembanding",
        "nilai_utama",
        "nilai_pembanding",
        "satuan_utama",
        "satuan_pembanding",
        "selisih",
        "berpasangan",
        "kategori_penjelasan",
        "catatan",
        "dugaan",
        "bukti_dicari",
        "_berkas_raw_utama",
        "_sha256_raw_utama",
        "_berkas_raw_pembanding",
        "_sha256_raw_pembanding",
    ]
    tabel = tabel[kolom]
    gold = Path(gold)
    gold.mkdir(parents=True, exist_ok=True)
    tabel.to_parquet(gold / "rekonsiliasi_nasional.parquet", index=False)
    return tabel


def median_selisih(tabel_rekonsiliasi):
    """Median selisih bertanda untuk pasangan var1410 (satuan sama: persen)."""
    t = tabel_rekonsiliasi
    selisih = t.loc[t["berpasangan"] & t["seri_utama"].eq("var1410"), "selisih"].dropna()
    if selisih.empty:
        raise ValueError("Tidak ada periode berpasangan var1410.")
    return float(selisih.median())
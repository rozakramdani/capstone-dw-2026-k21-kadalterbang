"""Bentuk grid provinsi x tahun dari Silver dan laporkan kelengkapannya."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver" / "silver.parquet"
GOLD = ROOT / "data" / "gold"
TABLES = ROOT / "reports" / "tables"

PROVINSI = {
    "1100": "ACEH",
    "1200": "SUMATERA UTARA",
    "1300": "SUMATERA BARAT",
    "1400": "RIAU",
    "1500": "JAMBI",
    "1600": "SUMATERA SELATAN",
    "1700": "BENGKULU",
    "1800": "LAMPUNG",
    "1900": "KEP. BANGKA BELITUNG",
    "2100": "KEP. RIAU",
    "3100": "DKI JAKARTA",
    "3200": "JAWA BARAT",
    "3300": "JAWA TENGAH",
    "3400": "DI YOGYAKARTA",
    "3500": "JAWA TIMUR",
    "3600": "BANTEN",
    "5100": "BALI",
    "5200": "NUSA TENGGARA BARAT",
    "5300": "NUSA TENGGARA TIMUR",
    "6100": "KALIMANTAN BARAT",
    "6200": "KALIMANTAN TENGAH",
    "6300": "KALIMANTAN SELATAN",
    "6400": "KALIMANTAN TIMUR",
    "6500": "KALIMANTAN UTARA",
    "7100": "SULAWESI UTARA",
    "7200": "SULAWESI TENGAH",
    "7300": "SULAWESI SELATAN",
    "7400": "SULAWESI TENGGARA",
    "7500": "GORONTALO",
    "7600": "SULAWESI BARAT",
    "8100": "MALUKU",
    "8200": "MALUKU UTARA",
    "9100": "PAPUA BARAT",
    "9200": "PAPUA BARAT DAYA",
    "9400": "PAPUA",
    "9500": "PAPUA SELATAN",
    "9600": "PAPUA TENGAH",
    "9700": "PAPUA PEGUNUNGAN",
}
KODE_INDONESIA = "9999"
SERI = ("var1311", "var1312", "var1410", "var1831", "var2738", "var2740")


def _baca_silver(path):
    df = pd.read_parquet(path)
    wajib = {
        "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "rincian",
        "nilai", "_berkas_raw",
    }
    hilang = wajib - set(df.columns)
    if hilang:
        raise ValueError(f"Kolom Silver tidak lengkap: {sorted(hilang)}")
    df = df[df["seri_kode"].isin(SERI)].copy()
    df["wilayah_kode"] = df["wilayah_kode"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["nama_wilayah"] = df["nama_wilayah"].astype(str).str.strip().str.upper()
    df["periode"] = df["periode"].astype(str).str.strip()
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    df["_snapshot"] = df["_berkas_raw"].str.extract(r"(\d{4}-\d{2}-\d{2})")
    if df["_snapshot"].isna().any():
        raise ValueError("Tanggal snapshot tidak dapat ditentukan dari _berkas_raw.")
    terbaru_per_seri = df.groupby("seri_kode")["_snapshot"].transform("max")
    df = df[df["_snapshot"] == terbaru_per_seri].drop(columns="_snapshot")

    kode_tidak_dikenal = set(df["wilayah_kode"]) - set(PROVINSI) - {KODE_INDONESIA}
    if kode_tidak_dikenal:
        raise ValueError(f"Kode wilayah belum dipetakan: {sorted(kode_tidak_dikenal)}")
    salah_nama = df[df["wilayah_kode"].isin(PROVINSI)].loc[
        lambda baris: baris["nama_wilayah"]
        != baris["wilayah_kode"].map(PROVINSI)
    ]
    if not salah_nama.empty:
        raise ValueError(
            "Kode dan nama provinsi tidak cocok: "
            f"{salah_nama[['wilayah_kode', 'nama_wilayah']].drop_duplicates().to_dict('records')}"
        )
    return df


def bentuk_grid(silver=SILVER, gold=GOLD, tables=TABLES):
    df = _baca_silver(silver)
    provinsi = df[df["wilayah_kode"] != KODE_INDONESIA].copy()
    indonesia = df[df["wilayah_kode"] == KODE_INDONESIA].copy()
    if provinsi.empty:
        raise ValueError("Silver tidak memiliki baris provinsi untuk seri kasus ini.")

    if provinsi.duplicated(["seri_kode", "wilayah_kode", "periode", "rincian"]).any():
        raise ValueError("Silver masih memiliki duplikat kunci seri-wilayah-periode-rincian.")

    observasi = provinsi[
        ["seri_kode", "wilayah_kode", "nama_wilayah", "periode", "rincian", "nilai"]
    ]
    rincian_per_seri = observasi.groupby("seri_kode")["rincian"].unique().to_dict()
    bingkai = []
    for seri in SERI:
        data_seri = observasi[observasi["seri_kode"] == seri]
        if data_seri.empty:
            raise ValueError(f"Seri {seri} tidak ditemukan di Silver.")
        for rincian in rincian_per_seri[seri]:
            tahun_terbit = sorted(data_seri.loc[data_seri["rincian"] == rincian, "periode"].unique())
            kerangka = pd.MultiIndex.from_product(
                [tahun_terbit, list(PROVINSI)],
                names=["periode", "wilayah_kode"],
            ).to_frame(index=False)
            kerangka.insert(0, "seri_kode", seri)
            kerangka["rincian"] = rincian
            bingkai.append(kerangka)

    grid = pd.concat(bingkai, ignore_index=True)
    grid["nama_wilayah"] = grid["wilayah_kode"].map(PROVINSI)
    grid = grid.merge(
        observasi,
        on=["seri_kode", "wilayah_kode", "nama_wilayah", "periode", "rincian"],
        how="left",
        validate="one_to_one",
    )
    grid["tersedia"] = grid["nilai"].notna()
    grid = grid.sort_values(["seri_kode", "periode", "wilayah_kode"]).reset_index(drop=True)

    matriks = (
        grid.groupby(["seri_kode", "periode", "rincian"], as_index=False)
        .agg(provinsi_terisi=("tersedia", "sum"))
    )
    matriks["jumlah_provinsi"] = len(PROVINSI)
    matriks["sel_kosong"] = matriks["jumlah_provinsi"] - matriks["provinsi_terisi"]
    matriks["persen_sel_terisi"] = (
        matriks["provinsi_terisi"] / matriks["jumlah_provinsi"] * 100
    ).round(2)
    matriks = matriks[
        [
            "seri_kode",
            "periode",
            "rincian",
            "provinsi_terisi",
            "jumlah_provinsi",
            "sel_kosong",
            "persen_sel_terisi",
        ]
    ].sort_values(["seri_kode", "periode", "rincian"])

    gold.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    grid.to_parquet(gold / "grid_provinsi.parquet", index=False)
    indonesia.sort_values(["seri_kode", "periode"]).to_parquet(
        gold / "indonesia_terpisah.parquet", index=False
    )
    matriks.to_csv(tables / "matriks_ketersediaan_panel.csv", index=False)
    return grid, indonesia, matriks


if __name__ == "__main__":
    grid, indonesia, matriks = bentuk_grid()
    print(f"Grid provinsi: {len(grid)} sel; baris Indonesia terpisah: {len(indonesia)}")
    print(f"Sel kosong dalam tahun terbit: {int(matriks['sel_kosong'].sum())}")
    print(matriks.to_string(index=False))

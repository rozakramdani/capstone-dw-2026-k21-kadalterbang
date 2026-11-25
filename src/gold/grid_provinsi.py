"""Pilih satu observasi Gold per provinsi-tahun-seri dan bentuk grid lengkap."""
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver" / "silver.parquet"
GOLD = ROOT / "data" / "gold"
TABLES = ROOT / "reports" / "tables"
ANOMALI = TABLES / "calon_anomali.csv"
PATAHAN = TABLES / "patahan_seri.csv"

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
RINCIAN_PANEL = {seri: "Tidak ada" for seri in SERI}
POLA_PERIODE = {
    "tahun": re.compile(r"^(\d{4})$"),
    "semester": re.compile(r"^(\d{4})-S[12]$"),
    "triwulan": re.compile(r"^(\d{4})-Q[1-4]$"),
    "bulan": re.compile(r"^(\d{4})-(?:0[1-9]|1[0-2])$"),
}


def _baca_silver(path):
    df = pd.read_parquet(path)
    wajib = {
        "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "rincian",
        "nilai", "_berkas_raw",
    }
    hilang = wajib - set(df.columns)
    if hilang:
        raise ValueError(f"Kolom Silver tidak lengkap: {sorted(hilang)}")
    df = df[df["seri_kode"].isin(SERI)].copy()
    df["wilayah_kode"] = df["wilayah_kode"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["nama_wilayah"] = df["nama_wilayah"].astype(str).str.strip().str.upper()
    df["periode"] = df["periode"].astype(str).str.strip()
    df["jenis_periode"] = df["jenis_periode"].astype(str).str.strip().str.lower()
    df["rincian"] = df["rincian"].astype(str).str.strip()
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    df["_snapshot"] = df["_berkas_raw"].str.extract(r"(\d{4}-\d{2}-\d{2})")
    if df["_snapshot"].isna().any():
        raise ValueError("Tanggal snapshot tidak dapat ditentukan dari _berkas_raw.")

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


def _tahun_periode(periode, jenis):
    pola = POLA_PERIODE.get(jenis)
    if pola is None:
        raise ValueError(f"Jenis periode tidak didukung Gold: {jenis}")
    cocok = pola.fullmatch(str(periode))
    if not cocok:
        raise ValueError(f"Periode {periode!r} tidak sesuai jenis {jenis}.")
    return int(cocok.group(1))


def _baca_penanda(calon_anomali, patahan):
    calon = pd.read_csv(calon_anomali, dtype={"wilayah_kode": str, "snapshot": str})
    kolom_calon = {
        "seri_kode", "wilayah_kode", "periode", "rincian", "snapshot", "kategori"
    }
    if not kolom_calon.issubset(calon.columns):
        raise ValueError(
            "Tabel calon anomali belum memuat kolom untuk lineage Gold: "
            f"{sorted(kolom_calon - set(calon.columns))}"
        )
    calon["wilayah_kode"] = calon["wilayah_kode"].str.replace(r"\.0$", "", regex=True)
    calon["periode"] = calon["periode"].astype(str).str.strip()
    calon["rincian"] = calon["rincian"].astype(str).str.strip()
    calon["snapshot"] = calon["snapshot"].astype(str).str.strip()
    calon_kunci = ["seri_kode", "wilayah_kode", "periode", "rincian", "snapshot"]
    if calon.duplicated(calon_kunci).any():
        raise ValueError("Tabel calon anomali memiliki kunci observasi Gold ganda.")

    indikasi = pd.read_csv(patahan, dtype={"snapshot": str})
    kolom_patahan = {"seri_kode", "snapshot", "tahun"}
    if not kolom_patahan.issubset(indikasi.columns):
        raise ValueError(
            "Tabel patahan seri belum memuat kolom wajib: "
            f"{sorted(kolom_patahan - set(indikasi.columns))}"
        )
    indikasi["snapshot"] = indikasi["snapshot"].astype(str).str.strip()
    indikasi["tahun"] = pd.to_numeric(indikasi["tahun"], errors="raise").astype(int)
    return calon, indikasi


def pilih_observasi_gold(
    silver,
    calon_anomali=ANOMALI,
    patahan=PATAHAN,
):
    """Terapkan snapshot, rincian, periode, dan penanda secara deterministik."""
    data = _baca_silver(silver) if isinstance(silver, (str, Path)) else silver.copy()
    data = data[data["seri_kode"].isin(SERI)].copy()
    seri_ada = set(data["seri_kode"])
    if seri_ada != set(SERI):
        raise ValueError(f"Seri Silver tidak cocok: {sorted(seri_ada)}")

    jumlah_silver = len(data)
    snapshot_terbaru = data.groupby("seri_kode")["_snapshot"].max()
    snapshot_lama = data["seri_kode"].map(snapshot_terbaru) != data["_snapshot"]
    baris_snapshot_tidak_dipilih = int(snapshot_lama.sum())
    data = data.loc[~snapshot_lama].copy()

    rincian_terpilih = data["seri_kode"].map(RINCIAN_PANEL)
    rincian_tidak_cocok = data["rincian"] != rincian_terpilih
    baris_rincian_tidak_dipilih = int(rincian_tidak_cocok.sum())
    data = data.loc[~rincian_tidak_cocok].copy()
    for seri, rincian in RINCIAN_PANEL.items():
        if not data.loc[data["seri_kode"] == seri].shape[0]:
            raise ValueError(f"Rincian panel {rincian!r} tidak ditemukan untuk {seri}.")

    data["_tahun"] = [
        _tahun_periode(periode, jenis)
        for periode, jenis in zip(data["periode"], data["jenis_periode"])
    ]
    data["snapshot"] = data["_snapshot"]
    kunci_observasi = ["seri_kode", "wilayah_kode", "periode", "rincian"]
    if data.duplicated(kunci_observasi).any():
        duplikat = data.loc[
            data.duplicated(kunci_observasi, keep=False), kunci_observasi
        ].drop_duplicates()
        raise ValueError(
            "Ambiguitas dalam snapshot terbaru setelah pemilihan rincian; "
            f"perlu rekonsiliasi Silver: {duplikat.head(5).to_dict('records')}"
        )

    calon, indikasi = _baca_penanda(calon_anomali, patahan)
    kunci_calon = ["seri_kode", "wilayah_kode", "periode", "rincian", "snapshot"]
    data = data.merge(
        calon[kunci_calon + ["kategori"]].rename(
            columns={"kategori": "kategori_anomali"}
        ),
        on=kunci_calon,
        how="left",
        validate="one_to_one",
    )
    data["flag_kandidat_anomali"] = data["kategori_anomali"].notna()
    data["flag_outlier"] = data["kategori_anomali"].eq("outlier_asli")
    data["flag_galat_input"] = data["kategori_anomali"].eq("galat_input")
    tahun_patahan = set(
        zip(indikasi["seri_kode"], indikasi["snapshot"], indikasi["tahun"])
    )
    data["flag_patahan_seri"] = [
        (seri, snap, tahun) in tahun_patahan or kategori == "patahan_seri"
        for seri, snap, tahun, kategori in zip(
            data["seri_kode"], data["_snapshot"], data["_tahun"], data["kategori_anomali"]
        )
    ]

    baris_subtahunan_tidak_dipilih = int((data["jenis_periode"] != "tahun").sum())
    data = data[data["jenis_periode"] == "tahun"].copy()
    jumlah_periode_sumber = len(data)

    grup_kunci = ["seri_kode", "wilayah_kode", "_tahun"]
    hasil = []
    for kunci, grup in data.groupby(grup_kunci, sort=True, dropna=False):
        satuan = grup["satuan"].drop_duplicates()
        if len(satuan) != 1:
            raise ValueError(f"Satuan tidak konsisten dalam sel Gold {kunci}: {satuan.tolist()}")
        sumber = grup.sort_values("periode")
        categories = sorted(grup["kategori_anomali"].dropna().unique())
        baris = {
            "seri_kode": kunci[0],
            "wilayah_kode": kunci[1],
            "_tahun": kunci[2],
            "nama_wilayah": grup["nama_wilayah"].iloc[0],
            "rincian": grup["rincian"].iloc[0],
            "nilai": grup["nilai"].mean(),
            "satuan": satuan.iloc[0],
            "snapshot": grup["_snapshot"].iloc[0],
            "periode_sumber": ";".join(sumber["periode"].astype(str)),
            "jumlah_periode_sumber": len(grup),
            "_berkas_raw": ";".join(sumber["_berkas_raw"].astype(str)),
            "_sha256_raw": ";".join(sumber["_sha256_raw"].astype(str)),
            "kategori_anomali": ";".join(categories),
            "flag_kandidat_anomali": bool(grup["flag_kandidat_anomali"].any()),
            "flag_outlier": bool(grup["flag_outlier"].any()),
            "flag_galat_input": bool(grup["flag_galat_input"].any()),
            "flag_patahan_seri": bool(grup["flag_patahan_seri"].any()),
        }
        hasil.append(baris)
    terpilih = pd.DataFrame(hasil)
    terpilih["periode"] = terpilih["_tahun"].astype(str)
    terpilih = terpilih.drop(columns="_tahun")
    if terpilih.duplicated(["seri_kode", "wilayah_kode", "periode"]).any():
        raise ValueError("Pemilihan Gold menghasilkan lebih dari satu baris per sel indikator.")
    if len(terpilih) > jumlah_periode_sumber:
        raise ValueError("Jumlah observasi Gold melebihi baris sumber yang dipilih.")

    ringkasan = {
        "baris_silver_seri_kasus": jumlah_silver,
        "baris_snapshot_lama_tidak_dipilih": baris_snapshot_tidak_dipilih,
        "baris_rincian_tidak_dipilih": baris_rincian_tidak_dipilih,
        "baris_subtahunan_tidak_dipilih": baris_subtahunan_tidak_dipilih,
        "baris_periode_sumber_digabungkan": jumlah_periode_sumber - len(terpilih),
        "baris_gold_observasi": len(terpilih),
        "baris_kandidat_anomali_gold": int(terpilih["flag_kandidat_anomali"].sum()),
        "baris_patahan_gold": int(terpilih["flag_patahan_seri"].sum()),
    }
    return terpilih, ringkasan


def bentuk_grid(
    silver=SILVER,
    gold=GOLD,
    tables=TABLES,
    calon_anomali=ANOMALI,
    patahan=PATAHAN,
):
    observasi, ringkasan = pilih_observasi_gold(
        silver, calon_anomali=calon_anomali, patahan=patahan
    )
    provinsi = observasi[observasi["wilayah_kode"] != KODE_INDONESIA].copy()
    indonesia = observasi[observasi["wilayah_kode"] == KODE_INDONESIA].copy()
    if provinsi.empty:
        raise ValueError("Silver tidak memiliki baris provinsi untuk seri kasus ini.")

    bingkai = []
    for seri in SERI:
        data_seri = provinsi[provinsi["seri_kode"] == seri]
        if data_seri.empty:
            raise ValueError(f"Seri {seri} tidak ditemukan di Silver.")
        tahun_terbit = sorted(data_seri["periode"].unique())
        kerangka = pd.MultiIndex.from_product(
            [tahun_terbit, list(PROVINSI)],
            names=["periode", "wilayah_kode"],
        ).to_frame(index=False)
        kerangka.insert(0, "seri_kode", seri)
        bingkai.append(kerangka)

    grid = pd.concat(bingkai, ignore_index=True)
    grid["nama_wilayah"] = grid["wilayah_kode"].map(PROVINSI)
    kolom_observasi = [
        "seri_kode", "wilayah_kode", "periode", "nama_wilayah", "rincian", "nilai",
        "satuan", "snapshot", "periode_sumber", "jumlah_periode_sumber",
        "_berkas_raw", "_sha256_raw", "kategori_anomali", "flag_kandidat_anomali",
        "flag_outlier", "flag_galat_input", "flag_patahan_seri",
    ]
    grid = grid.merge(
        provinsi[kolom_observasi],
        on=["seri_kode", "wilayah_kode", "nama_wilayah", "periode"],
        how="left",
        validate="one_to_one",
    )
    for kolom in [
        "flag_kandidat_anomali", "flag_outlier", "flag_galat_input", "flag_patahan_seri"
    ]:
        grid[kolom] = grid[kolom].astype("boolean").fillna(False).astype(bool)
    grid["kategori_anomali"] = grid["kategori_anomali"].fillna("")
    grid["tersedia"] = grid["nilai"].notna()
    grid = grid.sort_values(["seri_kode", "periode", "wilayah_kode"]).reset_index(drop=True)
    if grid.duplicated(["seri_kode", "wilayah_kode", "periode"]).any():
        raise ValueError("Gold grid memiliki duplikat seri-provinsi-periode.")

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
    pd.DataFrame([ringkasan]).to_csv(tables / "pemilihan_gold.csv", index=False)
    return grid, indonesia, matriks, ringkasan


if __name__ == "__main__":
    grid, indonesia, matriks, ringkasan = bentuk_grid()
    print(f"Grid provinsi: {len(grid)} sel; baris Indonesia terpisah: {len(indonesia)}")
    print(f"Sel kosong dalam tahun terbit: {int(matriks['sel_kosong'].sum())}")
    print(f"Pemilihan Gold: {ringkasan}")
    print(matriks.to_string(index=False))

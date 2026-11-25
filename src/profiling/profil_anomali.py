"""Profil kandidat anomali dan klasifikasi setelah Silver mempertahankan snapshot."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver" / "silver.parquet"
TABLES = ROOT / "reports" / "tables"
GAMBAR = ROOT / "reports" / "gambar"
SERI_LIST = ("var1311", "var1312", "var2738", "var2740", "var1410", "var1831")
AMBANG_KONSENSUS = 0.95
AMBANG_LONJAKAN = 0.03


def _baca_snapshot(path):
    df = pd.read_parquet(path)
    df = df[df["seri_kode"].isin(SERI_LIST)].copy()
    df["wilayah_kode"] = df["wilayah_kode"].astype(str).str.replace(
        r"\.0$", "", regex=True
    )
    df["_snapshot"] = df["_berkas_raw"].str.extract(r"(\d{4}-\d{2}-\d{2})")
    if df["_snapshot"].isna().any():
        raise ValueError("Tanggal snapshot tidak dapat ditentukan dari _berkas_raw.")
    df = df[df["wilayah_kode"] != "9999"].copy()
    df["periode"] = df["periode"].astype(str).str.strip()
    df["_tahun"] = pd.to_numeric(
        df["periode"].str.extract(r"^(\d{4})")[0], errors="raise"
    ).astype(int)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    if df.duplicated(
        ["seri_kode", "_snapshot", "wilayah_kode", "periode", "rincian"]
    ).any():
        raise ValueError("Silver memiliki kunci seri-snapshot-wilayah-tahun-rincian ganda.")
    return df


def _patahan_seri(df):
    hasil = []
    for (seri, snapshot), data in df.groupby(["seri_kode", "_snapshot"]):
        panel = (
            data.groupby(["_tahun", "wilayah_kode"])["nilai"]
            .mean()
            .unstack()
            .sort_index()
        )
        for tahun in panel.index:
            if tahun - 1 not in panel.index:
                continue
            sebelumnya = panel.loc[tahun - 1]
            perubahan = (panel.loc[tahun] - sebelumnya).dropna()
            sebelumnya = sebelumnya.loc[perubahan.index]
            if perubahan.empty:
                continue
            konsensus = max((perubahan > 0).mean(), (perubahan < 0).mean())
            perubahan_median = perubahan.median()
            nilai_median_sebelumnya = sebelumnya.median()
            lonjakan = (
                abs(perubahan_median) / abs(nilai_median_sebelumnya)
                if nilai_median_sebelumnya
                else 0
            )
            if konsensus >= AMBANG_KONSENSUS and lonjakan >= AMBANG_LONJAKAN:
                hasil.append({
                    "seri_kode": seri,
                    "snapshot": snapshot,
                    "tahun": tahun,
                    "provinsi_dibandingkan": len(perubahan),
                    "konsensus_arah": round(konsensus, 4),
                    "perubahan_median": round(perubahan_median, 4),
                    "lonjakan_relatif": round(lonjakan, 4),
                    "kategori": "indikasi_patahan_seri",
                    "penjelasan": (
                        "Sekurangnya 95% provinsi bergerak searah dan perubahan median "
                        "mencapai 3% dari median tahun sebelumnya; nilai dipertahankan "
                        "karena sumber tidak mengonfirmasi perubahan metode."
                    ),
                })
    return pd.DataFrame(hasil)


def _profil_satu_seri(seri, snapshot, data_seri, patahan):
    q1 = data_seri["nilai"].quantile(0.25)
    q3 = data_seri["nilai"].quantile(0.75)
    iqr = q3 - q1
    mean = data_seri["nilai"].mean()
    std = data_seri["nilai"].std()

    calon = data_seri[
        (data_seri["nilai"] < q1 - 1.5 * iqr)
        | (data_seri["nilai"] > q3 + 1.5 * iqr)
        | ((data_seri["nilai"] - mean).abs() > 3 * std if std > 0 else False)
    ].copy()

    baris = []
    tahun_patahan = set(
        patahan.loc[
            (patahan["seri_kode"] == seri) & (patahan["snapshot"] == snapshot),
            "tahun",
        ].tolist()
    ) if not patahan.empty else set()
    for _, row in calon.iterrows():
        alasan = []
        if row["nilai"] < q1 - 1.5 * iqr or row["nilai"] > q3 + 1.5 * iqr:
            alasan.append("IQR")
        if std > 0 and abs(row["nilai"] - mean) > 3 * std:
            alasan.append("Z-Score")

        if row["_tahun"] in tahun_patahan:
            kategori = "patahan_seri"
            penjelasan = (
                "Nilai berada pada tahun dengan lonjakan serentak antarprovinsi; "
                "ditandai untuk telaah definisi/metode dan tidak dikoreksi."
            )
        elif row["nilai"] < 0 or row["nilai"] > 100:
            kategori = "galat_input"
            penjelasan = (
                "Nilai di luar domain indikator 0-100; perlu verifikasi ke berkas sumber "
                "sebelum koreksi."
            )
        else:
            kategori = "outlier_asli"
            penjelasan = (
                "Nilai ekstrem masih berada dalam domain indikator dan cocok dengan "
                "snapshot sumber; dipertahankan, bukan dihapus atau diimputasi."
            )
        baris.append({
            "seri_kode": seri,
            "wilayah_kode": row["wilayah_kode"],
            "nama_wilayah": row["nama_wilayah"],
            "periode": row["periode"],
            "rincian": row["rincian"],
            "nilai": row["nilai"],
            "snapshot": snapshot,
            "alasan": ", ".join(alasan),
            "kategori": kategori,
            "penjelasan": penjelasan,
        })
    return calon, baris


def jalankan_profiling(silver=SILVER, tables=TABLES, gambar=GAMBAR):
    data = _baca_snapshot(silver)
    tables.mkdir(parents=True, exist_ok=True)
    gambar.mkdir(parents=True, exist_ok=True)

    patahan = _patahan_seri(data)
    profil_seri = []
    semua_anomali = []

    seri_tersedia = set(data["seri_kode"])
    if seri_tersedia != set(SERI_LIST):
        raise ValueError(f"Seri di Silver tidak cocok: {sorted(seri_tersedia)}")
    snapshot_terbaru = data.groupby("seri_kode")["_snapshot"].max().to_dict()

    for (seri, snapshot), data_seri in data.groupby(["seri_kode", "_snapshot"]):
        data_seri = data_seri.copy()
        calon, anomali = _profil_satu_seri(seri, snapshot, data_seri, patahan)
        semua_anomali.extend(anomali)
        profil_seri.append({
            "seri_kode": seri,
            "snapshot": snapshot,
            "n_baris": len(data_seri),
            "min": data_seri["nilai"].min(),
            "max": data_seri["nilai"].max(),
            "mean": data_seri["nilai"].mean(),
            "median": data_seri["nilai"].median(),
            "std": data_seri["nilai"].std(),
            "calon_anomali": len(calon),
        })

        if snapshot == snapshot_terbaru[seri]:
            fig, ax = plt.subplots(figsize=(10, 6))
            data_seri.boxplot(column="nilai", by="periode", ax=ax, grid=False)
            fig.suptitle("")
            ax.set_title(f"Boxplot {seri} — snapshot {snapshot}")
            ax.tick_params(axis="x", labelrotation=45)
            fig.tight_layout()
            plt.savefig(gambar / f"boxplot_{seri}.png")
            plt.close()

            fig, ax = plt.subplots(figsize=(12, 6))
            for _, wilayah in data_seri.groupby("wilayah_kode"):
                wilayah = wilayah.sort_values("periode")
                ax.plot(wilayah["periode"], wilayah["nilai"], alpha=0.3)
            median_per_tahun = data_seri.groupby("periode")["nilai"].median().reset_index()
            ax.plot(
                median_per_tahun["periode"],
                median_per_tahun["nilai"],
                color="red",
                linewidth=3,
                label="Median",
            )
            ax.set_title(f"Deret waktu {seri} per provinsi")
            ax.tick_params(axis="x", labelrotation=45)
            ax.legend()
            fig.tight_layout()
            plt.savefig(gambar / f"deret_waktu_{seri}.png")
            plt.close()

    pd.DataFrame(profil_seri).to_csv(tables / "profil_seri.csv", index=False)
    pd.DataFrame(semua_anomali).to_csv(tables / "calon_anomali.csv", index=False)
    patahan.to_csv(tables / "patahan_seri.csv", index=False)
    print(
        f"Profil selesai: {len(semua_anomali)} calon anomali, "
        f"{len(patahan)} indikasi patahan; seluruh nilai dipertahankan."
    )


if __name__ == "__main__":
    jalankan_profiling()

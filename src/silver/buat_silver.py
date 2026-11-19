import pandas as pd
import os
import re
from src import ekstraksi


def tentukan_jenis_periode(periode_str):
    """Fungsi bantuan untuk menebak jenis periode berdasarkan format teks."""
    periode_str = str(periode_str)
    if re.search(r'S[1-2]', periode_str, re.IGNORECASE):
        return 'semester'
    elif re.search(r'Q[1-4]', periode_str, re.IGNORECASE):
        return 'triwulan'
    elif '-' in periode_str and len(periode_str) >= 6:
        return 'bulan'
    else:
        return 'tahun' # Diubah dari 'tahunan' menjadi 'tahun' agar lolos skema


def _ringkas_snapshot(df):
    kunci = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]
    ringkasan = []
    revisi = []

    for seri, data_seri in df.groupby("seri_kode"):
        snapshot = sorted(data_seri["_snapshot"].unique())
        if len(snapshot) == 1:
            pasangan = [(None, snapshot[0])]
        else:
            pasangan = list(zip(snapshot, snapshot[1:]))

        for lama, baru in pasangan:
            terbaru = data_seri[data_seri["_snapshot"] == baru]
            if lama is None:
                ringkasan.append({
                    "seri_kode": seri,
                    "snapshot_lama": "",
                    "snapshot_baru": baru,
                    "baris_snapshot_lama": 0,
                    "baris_snapshot_baru": len(terbaru),
                    "nilai_sama": 0,
                    "revisi": 0,
                    "hanya_snapshot_lama": 0,
                    "hanya_snapshot_baru": len(terbaru),
                })
                continue

            sebelumnya = data_seri[data_seri["_snapshot"] == lama]
            gabung = sebelumnya[kunci + ["nilai"]].merge(
                terbaru[kunci + ["nilai"]],
                on=kunci,
                how="outer",
                suffixes=("_lama", "_baru"),
                indicator=True,
                validate="one_to_one",
            )
            sama = gabung["_merge"].eq("both") & gabung["nilai_lama"].eq(gabung["nilai_baru"])
            berubah = gabung["_merge"].eq("both") & ~sama
            for _, baris in gabung[berubah].iterrows():
                revisi.append({
                    "seri_kode": seri,
                    "wilayah_kode": baris["wilayah_kode"],
                    "periode": baris["periode"],
                    "rincian": baris["rincian"],
                    "snapshot_lama": lama,
                    "nilai_lama": baris["nilai_lama"],
                    "snapshot_baru": baru,
                    "nilai_baru": baris["nilai_baru"],
                })
            ringkasan.append({
                "seri_kode": seri,
                "snapshot_lama": lama,
                "snapshot_baru": baru,
                "baris_snapshot_lama": len(sebelumnya),
                "baris_snapshot_baru": len(terbaru),
                "nilai_sama": int(sama.sum()),
                "revisi": int(berubah.sum()),
                "hanya_snapshot_lama": int(gabung["_merge"].eq("left_only").sum()),
                "hanya_snapshot_baru": int(gabung["_merge"].eq("right_only").sum()),
            })

    return pd.DataFrame(ringkasan), pd.DataFrame(
        revisi,
        columns=[
            "seri_kode", "wilayah_kode", "periode", "rincian",
            "snapshot_lama", "nilai_lama", "snapshot_baru", "nilai_baru",
        ],
    )


def buat_silver():
    print("Memulai proses pembuatan Silver...")
    
    # 1. Panggil fungsi ekstraksi milik Rozak
    mentah = ekstraksi.jalankan()
    df = pd.concat(mentah.values(), ignore_index=True)
    print(f"Total baris mentah yang diekstrak: {len(df)}")
    
    # 2. Buang baris yang tidak memiliki nilai
    df = df.dropna(subset=['nilai']).copy()
    
    # 3. PEMETAAN KOLOM KE STANDAR SILVER
    df_silver = pd.DataFrame()
    
    # Perbaikan 1: Isi kolom 'sumber' berdasarkan _berkas_raw
    def dapatkan_sumber(berkas):
        if 'bps' in str(berkas).lower(): return 'bps'
        elif 'wdi' in str(berkas).lower(): return 'wdi'
        return 'unknown'
        
    df_silver['_berkas_raw'] = df['_berkas_raw']
    df_silver['_sha256_raw'] = df['_sha256_raw']
    df_silver['sumber'] = df['_berkas_raw'].apply(dapatkan_sumber)
    
    # Perbaikan 2: Pastikan wilayah_kode menjadi Integer
    wilayah_bersih = df['wilayah_id'].astype(str).str.replace(r'\.0$', '', regex=True)
    df_silver['wilayah_kode'] = pd.to_numeric(wilayah_bersih, errors='coerce').astype('Int64')
    df_silver['nama_wilayah'] = df['wilayah']
    
    df_silver['seri_kode'] = df['var_id'].astype(str).str.replace(r'\.0$', '', regex=True).apply(lambda x: f"var{x}" if x != 'nan' else x)
    df_silver['periode'] = df['tahun'].astype(str)
    
    # Perbaikan 3: panggil fungsi yang sudah diubah
    df_silver['jenis_periode'] = df_silver['periode'].apply(tentukan_jenis_periode)
    
    if 'turvar' in df.columns:
        df_silver['rincian'] = df['turvar'].fillna('total').astype(str)
    else:
        df_silver['rincian'] = 'total'
        
    df_silver['nilai'] = pd.to_numeric(df['nilai'].astype(str).str.replace(',', '.'), errors='coerce')
    df_silver['satuan'] = df['satuan'].fillna('tidak diketahui').astype(str)
    
    # Pastikan urutan kolom sesuai standar
    kolom_wajib = [
        'sumber', 'seri_kode', 'wilayah_kode', 'nama_wilayah', 
        'periode', 'jenis_periode', 'rincian', 'nilai', 
        'satuan', '_berkas_raw', '_sha256_raw'
    ]
    df_silver = df_silver[kolom_wajib]
    
    df_silver["_snapshot"] = df_silver["_berkas_raw"].str.extract(
        r"(\d{4}-\d{2}-\d{2})"
    )
    if df_silver["_snapshot"].isna().any():
        raise ValueError("Tanggal snapshot tidak dapat ditentukan dari _berkas_raw.")

    awal = len(df_silver)
    kunci_pengamatan = [
        "sumber", "_snapshot", "seri_kode", "wilayah_kode", "periode", "rincian"
    ]
    konflik = (
        df_silver.groupby(kunci_pengamatan, dropna=False)['nilai']
        .nunique(dropna=False)
    )
    konflik = konflik[konflik > 1]
    if not konflik.empty:
        raise ValueError(
            f"CSV/JSON berbeda dalam {len(konflik)} kunci pada snapshot yang sama; "
            "jangan deduplikasi sebelum sumber direkonsiliasi."
        )
    df_silver["_format_json"] = df_silver["_berkas_raw"].str.endswith(".json").astype(int)
    df_silver = (
        df_silver.sort_values(["_format_json", "_berkas_raw"])
        .drop_duplicates(subset=kunci_pengamatan, keep='last')
        .drop(columns=["_snapshot", "_format_json"])
    )
    print(
        f"Membuang {awal - len(df_silver)} salinan lintas format dalam snapshot; "
        "snapshot berbeda tetap dipertahankan."
    )

    df_silver["_snapshot"] = df_silver["_berkas_raw"].str.extract(
        r"(\d{4}-\d{2}-\d{2})"
    )
    ringkasan, revisi = _ringkas_snapshot(df_silver)
    df_silver = df_silver.drop(columns="_snapshot")
    
    # 4. Simpan ke Parquet
    os.makedirs("data/silver", exist_ok=True)
    os.makedirs("reports/tables", exist_ok=True)
    output_path = "data/silver/silver.parquet"
    df_silver.to_parquet(output_path, index=False)
    ringkasan.to_csv("reports/tables/perbandingan_snapshot.csv", index=False)
    revisi.to_csv("reports/tables/revisi_snapshot.csv", index=False)
    
    print(f"Berhasil menyimpan {len(df_silver)} baris ke {output_path}")
    print(f"Nilai yang berubah antar-snapshot dan dicatat sebagai revisi: {len(revisi)}")

if __name__ == "__main__":
    buat_silver()
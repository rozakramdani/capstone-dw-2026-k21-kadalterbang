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
    
    # CSV dan JSON pada snapshot yang sama adalah salinan pengamatan yang sama.
    awal = len(df_silver)
    kunci_pengamatan = ['sumber', 'seri_kode', 'wilayah_kode', 'periode', 'rincian']
    konflik = (
        df_silver.groupby(kunci_pengamatan, dropna=False)['nilai']
        .nunique(dropna=False)
    )
    konflik = konflik[konflik > 1]
    if not konflik.empty:
        raise ValueError(
            f"Nilai berbeda pada {len(konflik)} kunci pengamatan; "
            "perlu rekonsiliasi sumber sebelum membentuk Silver."
        )
    df_silver = (
        df_silver.sort_values('_berkas_raw')
        .drop_duplicates(subset=kunci_pengamatan, keep='last')
    )
    print(f"Membuang {awal - len(df_silver)} baris duplikat.")
    
    # 4. Simpan ke Parquet
    os.makedirs("data/silver", exist_ok=True)
    output_path = "data/silver/silver.parquet"
    df_silver.to_parquet(output_path, index=False)
    
    print(f"Berhasil menyimpan {len(df_silver)} baris ke {output_path}")

if __name__ == "__main__":
    buat_silver()
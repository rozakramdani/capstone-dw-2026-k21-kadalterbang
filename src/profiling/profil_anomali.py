import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from src import ekstraksi

os.makedirs("reports/gambar", exist_ok=True)
os.makedirs("reports/tables", exist_ok=True)

# Kita tetap simpan daftar seri aslinya
SERI_LIST = ['var1311', 'var1312', 'var2738', 'var2740', 'var1410', 'var1831']

def jalankan_profiling():
    print("Memanggil fungsi ekstraksi (membaca 26 file raw)...")
    mentah = ekstraksi.jalankan()
    
    df = pd.concat(mentah.values(), ignore_index=True)
    print(f"Total baris data mentah yang diekstrak: {len(df)}")
    
    # --- LANGKAH KUNCI 1: BERSIHKAN NILAI ---
    # Ubah kolom nilai menjadi numerik. Jika ada teks aneh (seperti '...' atau ','), jadikan NaN.
    df['nilai'] = pd.to_numeric(df['nilai'].astype(str).str.replace(',', '.'), errors='coerce')
    
    # Cek tipe data wilayah_id dan pastikan Indonesia (9999) dipisahkan
    df['wilayah_id_str'] = df['wilayah_id'].astype(str)
    df_prov = df[~df['wilayah_id_str'].isin(['9999', '9999.0'])].copy()

    # Cek format var_id untuk memastikan kita bisa memfilternya
    print(f"Contoh format var_id yang ada di data: {df_prov['var_id'].dropna().unique()[:5]}")

    profil_seri = []
    hasil_anomali = []

    for seri in SERI_LIST:
        print(f"\nMemproses Seri: {seri}...")
        
        # --- LANGKAH KUNCI 2: FILTER YANG LEBIH PINTAR ---
        # Ambil angka depannya saja (misal 'var1311' jadi '1311')
        kode_angka = seri.replace('var', '')
        
        # Cari baris yang var_id-nya mengandung angka tersebut
        data_seri = df_prov[df_prov['var_id'].astype(str).str.contains(kode_angka)].copy()
        
        # Buang nilai yang kosong (NaN)
        data_seri = data_seri.dropna(subset=['nilai'])
        
        if data_seri.empty:
            print(f"  -> Data kosong (var_id tidak ada yang cocok dengan {kode_angka}), dilewati.")
            continue

        print(f"  -> Ditemukan {len(data_seri)} baris data. Memproses statistik...")

        # --- A. STATISTIK DESKRIPTIF ---
        profil_seri.append({
            'seri_kode': seri,
            'n_baris': len(data_seri),
            'min': data_seri['nilai'].min(),
            'max': data_seri['nilai'].max(),
            'mean': data_seri['nilai'].mean(),
            'median': data_seri['nilai'].median(),
            'std': data_seri['nilai'].std()
        })

        # --- B. DETEKSI ANOMALI ---
        Q1 = data_seri['nilai'].quantile(0.25)
        Q3 = data_seri['nilai'].quantile(0.75)
        IQR = Q3 - Q1
        batas_bawah = Q1 - 1.5 * IQR
        batas_atas = Q3 + 1.5 * IQR
        
        mean = data_seri['nilai'].mean()
        std = data_seri['nilai'].std()
        
        if std == 0 or pd.isna(std): # Mencegah error jika semua nilainya sama
            std = 1
            
        anomali = data_seri[
            (data_seri['nilai'] < batas_bawah) | 
            (data_seri['nilai'] > batas_atas) |
            (data_seri['nilai'] > (mean + 3*std)) |
            (data_seri['nilai'] < (mean - 3*std))
        ]
        
        for _, row in anomali.iterrows():
            alasan = []
            if row['nilai'] < batas_bawah or row['nilai'] > batas_atas:
                alasan.append("IQR")
            if row['nilai'] > (mean + 3*std) or row['nilai'] < (mean - 3*std):
                alasan.append("Z-Score")
                
            hasil_anomali.append({
                'seri_kode': seri,
                'wilayah_kode': row.get('wilayah_id', 'N/A'),
                'nama_wilayah': row.get('wilayah', 'N/A'),
                'periode': row.get('periode', 'N/A'),
                'nilai': row['nilai'],
                'alasan': ", ".join(alasan)
            })

        # --- C. VISUALISASI ---
        # 1. Boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='periode', y='nilai', data=data_seri)
        plt.title(f'Boxplot {seri}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'reports/gambar/boxplot_{seri}.png')
        plt.close()

        # 2. Deret Waktu
        plt.figure(figsize=(12, 6))
        sns.lineplot(x='periode', y='nilai', hue='wilayah', data=data_seri, legend=False, alpha=0.3)
        
        median_per_periode = data_seri.groupby('periode')['nilai'].median().reset_index()
        if not median_per_periode.empty:
            sns.lineplot(x='periode', y='nilai', data=median_per_periode, color='red', linewidth=3, label='Median')
        
        plt.title(f'Deret Waktu {seri} per Provinsi')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'reports/gambar/deret_waktu_{seri}.png')
        plt.close()

    # Simpan hasil ke CSV
    pd.DataFrame(profil_seri).to_csv("reports/tables/profil_seri.csv", index=False)
    pd.DataFrame(hasil_anomali).to_csv("reports/tables/calon_anomali.csv", index=False)
    
    print("\n=== SELESAI ===")

if __name__ == "__main__":
    jalankan_profiling()
import pandas as pd
import os
from src import ekstraksi

def profil_pembanding():
    print("Memanggil fungsi ekstraksi untuk data WDI...")
    mentah = ekstraksi.jalankan()
    
    # 1. Ambil khusus data WDI
    # (Asumsi: kolom sumber di data mentah WDI berisi 'wdi' atau kita filter dari _berkas_raw)
    df_wdi = pd.DataFrame()
    
    for nama_berkas, df in mentah.items():
        if 'wdi' in nama_berkas.lower():
            if df_wdi.empty:
                df_wdi = df.copy()
            else:
                df_wdi = pd.concat([df_wdi, df], ignore_index=True)
                
    if df_wdi.empty:
        print("Data WDI tidak ditemukan di hasil ekstraksi.")
        return

    # 2. Filter hanya untuk Indonesia dan 2 seri pembanding yang diminta
    target_seri = ['VC.IHR.PSRC.P5', 'SP.REG.BRTH.ZS']
    
    # Di WDI, nama seri biasanya ada di kolom 'indicator.id'
    if 'indicator.id' in df_wdi.columns:
        df_target = df_wdi[df_wdi['indicator.id'].isin(target_seri)].copy()
    elif 'var_id' in df_wdi.columns:
        df_target = df_wdi[df_wdi['var_id'].isin(target_seri)].copy()
    else:
        print("Kolom indikator tidak ditemukan.")
        return

    # Filter hanya negara Indonesia
    df_target = df_target[df_target['country.value'] == 'Indonesia'].copy()
    
    # 3. Bersihkan kolom tahun (di WDI formatnya 'YR2015', kita ubah jadi '2015')
    if 'date' in df_target.columns:
        df_target['tahun'] = df_target['date'].astype(str).str.extract(r'(\d{4})')
    elif 'periode' in df_target.columns:
        df_target['tahun'] = df_target['periode'].astype(str).str.extract(r'(\d{4})')

    # 4. Buat tabel ketersediaan
    ketersediaan = []
    for seri in target_seri:
        if 'indicator.id' in df_target.columns:
            data_seri = df_target[df_target['indicator.id'] == seri]
        else:
            data_seri = df_target[df_target['var_id'] == seri]
            
        if data_seri.empty:
            continue
            
        tahun_unik = sorted(data_seri['tahun'].dropna().unique())
        satuan = data_seri['unit'].iloc[0] if 'unit' in data_seri.columns else "Tidak diketahui"
        
        # WDI biasanya tidak punya rincian sex/age untuk indikator ini (hanya total nasional)
        ketersediaan.append({
            'seri_pembanding': seri,
            'tahun_mulai': tahun_unik[0] if tahun_unik else 'N/A',
            'tahun_akhir': tahun_unik[-1] if tahun_unik else 'N/A',
            'jumlah_tahun_tersedia': len(tahun_unik),
            'daftar_tahun': ", ".join(tahun_unik),
            'satuan': satuan,
            'rincian': 'Total (National)'
        })

    df_ket = pd.DataFrame(ketersediaan)
    os.makedirs("reports/tables", exist_ok=True)
    df_ket.to_csv("reports/tables/profil_pembanding_wdi.csv", index=False)
    print("Berhasil menyimpan tabel ketersediaan di reports/tables/profil_pembanding_wdi.csv")
    print(df_ket)

if __name__ == "__main__":
    profil_pembanding()
from pathlib import Path

import pandas as pd


KATALOG = Path("data/katalog-seri.csv")


def baca_katalog():
    return pd.read_csv(KATALOG, dtype=str).fillna("tidak_ada")


def tentukan_katalog(seri_kode, satuan_fallback="tidak_ada"):
    katalog = baca_katalog()
    cocok = katalog.loc[katalog["seri_kode"].eq(str(seri_kode))]
    if cocok.empty:
        return {"nama_seri": "tidak_ada", "kode_sdg": "tidak_ada", "satuan": satuan_fallback}
    baris = cocok.iloc[0]
    return baris[["nama_seri", "kode_sdg", "satuan"]].to_dict()

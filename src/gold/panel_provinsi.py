"""Simpan panel provinsi tahunan dan matriks ketersediaan sebagai tabel Gold."""
from pathlib import Path

from src.gold.grid_provinsi import (
    ANOMALI,
    GOLD,
    PATAHAN,
    SILVER,
    TABLES,
    bentuk_grid,
)


def bentuk_panel_provinsi(
    silver=SILVER,
    gold=GOLD,
    tables=TABLES,
    calon_anomali=ANOMALI,
    patahan=PATAHAN,
):
    """Bangun dan simpan panel serta matriks ketersediaan dalam format Parquet."""
    panel, indonesia, matriks, ringkasan = bentuk_grid(
        silver=silver,
        gold=gold,
        tables=tables,
        calon_anomali=calon_anomali,
        patahan=patahan,
    )

    kunci = ["wilayah_kode", "periode", "seri_kode"]
    if panel.duplicated(kunci).any():
        raise ValueError(f"Panel Gold memiliki kunci duplikat: {kunci}")

    sumber = panel.loc[panel["tersedia"]]
    kolom_lineage = ["periode_sumber", "_berkas_raw", "_sha256_raw"]
    if sumber[kolom_lineage].isna().any().any():
        raise ValueError("Sel Gold terisi harus memiliki lineage ke baris Silver.")
    if sumber[kolom_lineage].astype(str).eq("").any().any():
        raise ValueError("Sel Gold terisi memiliki kolom lineage kosong.")
    if not panel["tersedia"].equals(panel["nilai"].notna()):
        raise ValueError("Flag ketersediaan Gold tidak sesuai dengan nilai.")

    gold = Path(gold)
    gold.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(gold / "panel_provinsi.parquet", index=False)
    matriks.to_parquet(gold / "matriks_ketersediaan_panel.parquet", index=False)
    return panel, indonesia, matriks, ringkasan


if __name__ == "__main__":
    panel, indonesia, matriks, ringkasan = bentuk_panel_provinsi()
    print(
        f"Panel provinsi: {len(panel)} baris; "
        f"{int(panel['tersedia'].sum())} sel terisi; "
        f"Indonesia terpisah: {len(indonesia)} baris"
    )
    print(f"Pemilihan Gold: {ringkasan}")
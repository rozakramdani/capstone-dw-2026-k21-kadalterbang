"""Tahap 8 — Validasi dan dokumentasi (pertemuan XIV–XV). Milik tim.

Tulis skema validasi Silver dan Gold (pandera atau Great Expectations): rentang nilai per satuan,
kelengkapan wilayah, keunikan kunci, konsistensi provinsi vs nasional bila relevan. Laporan
validasi ditulis ke reports/validasi.md. Data dictionary di docs/data-dictionary.md.
"""


"""Tahap 8 — Validasi dasar Silver dan Gold."""

from pathlib import Path

import pandera.pandas as pa


KOLOM_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]

KUNCI_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "periode",
    "rincian",
    "_berkas_raw",
]

KUNCI_GOLD = [
    "seri_kode",
    "wilayah_kode",
    "periode",
    "rincian",
]


def jalankan(silver, gold):
    """Menjalankan validasi dasar Silver dan Gold."""

    laporan = []
    aturan_lolos = 0

    def catat(nama, kondisi, detail):
        nonlocal aturan_lolos
        status = "LOLOS" if kondisi else "GAGAL"
        laporan.append(f"- {nama}: **{status}** — {detail}")
        if kondisi:
            aturan_lolos += 1

    # 1. Kelengkapan skema Silver
    skema = pa.DataFrameSchema(
        {
            kolom: pa.Column(nullable=False)
            for kolom in KOLOM_SILVER
        },
        strict=False,
    )

    try:
        skema.validate(silver, lazy=True)
        catat(
            "Kelengkapan skema Silver",
            True,
            "Seluruh kolom wajib tersedia dan tidak memiliki nilai kosong.",
        )
    except (pa.errors.SchemaErrors, pa.errors.SchemaError) as error:
        catat("Kelengkapan skema Silver", False, str(error))

    # 2. Rentang nilai persen
    mask_persen = silver["satuan"].str.contains(
        "persen", case=False, na=False
    )
    rentang_persen = (
        mask_persen.any()
        and silver.loc[mask_persen, "nilai"].between(0, 100).all()
    )
    catat(
        "Rentang nilai persen",
        rentang_persen,
        "Nilai dengan satuan persen harus berada pada rentang 0–100.",
    )

    # 3. Keunikan kunci Silver
    unik_silver = not silver.duplicated(subset=KUNCI_SILVER).any()
    catat(
        "Keunikan kunci Silver",
        unik_silver,
        "Tidak ditemukan duplikasi berdasarkan kunci Silver.",
    )

    # 4. Konsistensi satuan setiap seri
    konsisten_satuan = (
        silver.groupby("seri_kode")["satuan"]
        .nunique(dropna=False)
        .le(1)
        .all()
    )
    catat(
        "Konsistensi satuan",
        konsisten_satuan,
        "Setiap seri menggunakan satuan yang konsisten.",
    )

    # 5. Keunikan kunci Gold setelah aturan snapshot
    unik_gold = not gold.duplicated(subset=KUNCI_GOLD).any()
    catat(
        "Keunikan kunci Gold setelah snapshot",
        unik_gold,
        "Setiap kombinasi seri, wilayah, periode, dan rincian hanya muncul satu kali.",
    )

    # 6. Pemisahan seri pencatatan kelahiran
    seri_gold = set(gold["seri_kode"].unique())
    kelahiran_terpisah = (
        "var1410" in seri_gold and "var1831" in seri_gold
    )
    catat(
        "Pemisahan seri pencatatan kelahiran",
        kelahiran_terpisah,
        "var1410 dan var1831 tetap tercatat sebagai dua seri berbeda.",
    )

    # Menyimpan laporan
    Path("reports").mkdir(exist_ok=True)

    isi_laporan = [
        "# Laporan Validasi Silver dan Gold",
        "",
        f"- Jumlah baris Silver: {len(silver)}",
        f"- Jumlah seri Silver: {silver['seri_kode'].nunique()}",
        f"- Jumlah aturan: {len(laporan)}",
        f"- Aturan lolos: {aturan_lolos}",
        "",
        "## Hasil Pemeriksaan",
        "",
        *laporan,
        "",
    ]

    Path("reports/validasi.md").write_text(
        "\n".join(isi_laporan),
        encoding="utf-8",
    )

    print("\n".join(laporan))
    print(f"\nAturan lolos: {aturan_lolos}/{len(laporan)}")

    if aturan_lolos != len(laporan):
        raise ValueError(
            "Validasi gagal. Periksa reports/validasi.md."
        )

    return {
        "aturan_validasi": len(laporan),
        "aturan_lolos": aturan_lolos,
    }

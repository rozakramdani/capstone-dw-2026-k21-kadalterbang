CREATE TABLE IF NOT EXISTS silver_observasi (
    sumber TEXT NOT NULL,
    seri_kode TEXT NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah TEXT NOT NULL,
    periode TEXT NOT NULL,
    jenis_periode TEXT NOT NULL,
    rincian TEXT NOT NULL,
    nilai REAL NOT NULL,
    satuan TEXT NOT NULL,
    _berkas_raw TEXT NOT NULL,
    _sha256_raw TEXT NOT NULL,
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);

CREATE TABLE IF NOT EXISTS panel_provinsi (
    seri_kode TEXT NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    periode TEXT NOT NULL,
    nama_wilayah TEXT NOT NULL,
    rincian TEXT,
    nilai REAL,
    satuan TEXT NOT NULL,
    snapshot TEXT,
    periode_sumber TEXT,
    jumlah_periode_sumber INTEGER,
    _berkas_raw TEXT,
    _sha256_raw TEXT,
    kategori_anomali TEXT,
    flag_kandidat_anomali INTEGER NOT NULL CHECK (flag_kandidat_anomali IN (0, 1)),
    flag_outlier INTEGER NOT NULL CHECK (flag_outlier IN (0, 1)),
    flag_galat_input INTEGER NOT NULL CHECK (flag_galat_input IN (0, 1)),
    flag_patahan_seri INTEGER NOT NULL CHECK (flag_patahan_seri IN (0, 1)),
    tersedia INTEGER NOT NULL CHECK (tersedia IN (0, 1)),
    PRIMARY KEY (wilayah_kode, periode, seri_kode)
);

CREATE TABLE IF NOT EXISTS tabel_nasional (
    periode TEXT NOT NULL,
    seri_kode TEXT NOT NULL,
    sumber TEXT NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah TEXT NOT NULL,
    rincian TEXT NOT NULL,
    nilai REAL,
    satuan TEXT NOT NULL,
    asal_nilai TEXT NOT NULL,
    _berkas_raw TEXT NOT NULL,
    _sha256_raw TEXT NOT NULL,
    PRIMARY KEY (periode, seri_kode)
);

CREATE TABLE IF NOT EXISTS rekonsiliasi_nasional (
    periode INTEGER NOT NULL,
    seri_kode TEXT NOT NULL,
    sumber TEXT NOT NULL,
    nama_seri TEXT NOT NULL,
    nilai REAL NOT NULL,
    satuan TEXT NOT NULL,
    rincian TEXT NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah TEXT NOT NULL,
    _berkas_raw TEXT NOT NULL,
    _sha256_raw TEXT NOT NULL,
    PRIMARY KEY (periode, seri_kode)
);

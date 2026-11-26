
-- akun pengguna
CREATE TABLE IF NOT EXISTS pengguna (
    id        SERIAL PRIMARY KEY,
    username  VARCHAR(50) UNIQUE NOT NULL,
    password  VARCHAR(50) NOT NULL,
    peran     VARCHAR(20) NOT NULL
);

-- daftar menu dan stok
CREATE TABLE IF NOT EXISTS menu (
    id             SERIAL PRIMARY KEY,
    nama           VARCHAR(64) NOT NULL,
    kategori       VARCHAR(30) NOT NULL,
    harga          INTEGER NOT NULL,
    stok           INTEGER NOT NULL DEFAULT 0,
    batas_minimum  INTEGER NOT NULL DEFAULT 5,
    aktif          BOOLEAN NOT NULL DEFAULT TRUE
);

-- penawaran harga khusus anti-waste
CREATE TABLE IF NOT EXISTS anti_waste (
    id               SERIAL PRIMARY KEY,
    id_menu          INTEGER NOT NULL REFERENCES menu(id),
    harga_penawaran  INTEGER NOT NULL,
    batas_waktu      TIME NOT NULL,
    tanggal          DATE NOT NULL DEFAULT CURRENT_DATE,
    aktif            BOOLEAN NOT NULL DEFAULT TRUE
);

-- data transaksi penjualan
CREATE TABLE IF NOT EXISTS transaksi (
    id              SERIAL PRIMARY KEY,
    tanggal         TIMESTAMP NOT NULL DEFAULT NOW(),
    nomor_antrean   INTEGER NOT NULL,
    nama_pelanggan  VARCHAR(100) NOT NULL,
    total           INTEGER NOT NULL DEFAULT 0,
    dibayar         INTEGER NOT NULL DEFAULT 0,
    kembalian       INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'diproses'
);

-- rincian menu dalam transaksi
CREATE TABLE IF NOT EXISTS item_transaksi (
    id            SERIAL PRIMARY KEY,
    id_transaksi  INTEGER NOT NULL REFERENCES transaksi(id),
    id_menu       INTEGER NOT NULL REFERENCES menu(id),
    jumlah        INTEGER NOT NULL,
    harga_satuan  INTEGER NOT NULL
);

-- penyesuaian kolom database lama
ALTER TABLE transaksi ADD COLUMN IF NOT EXISTS dibayar   INTEGER NOT NULL DEFAULT 0;
ALTER TABLE transaksi ADD COLUMN IF NOT EXISTS kembalian INTEGER NOT NULL DEFAULT 0;
ALTER TABLE anti_waste ADD COLUMN IF NOT EXISTS tanggal  DATE NOT NULL DEFAULT CURRENT_DATE;

-- mengatur ulang seluruh data dummy
TRUNCATE item_transaksi, transaksi, anti_waste, menu, pengguna RESTART IDENTITY CASCADE;

-- data akun pengguna
INSERT INTO pengguna (username, password, peran) VALUES
('admin',  'admin123', 'admin'),
('kasir1', 'kasir123', 'karyawan'),
('kasir2', 'kasir456', 'karyawan');

-- data menu dan stok awal
INSERT INTO menu (nama, kategori, harga, stok, batas_minimum, aktif) VALUES
('Kopi Susu',       'Minuman', 18000, 23, 10, TRUE),
('Americano',       'Minuman', 15000, 22, 10, TRUE),
('Latte',           'Minuman', 22000, 17,  8, TRUE),
('Matcha Latte',    'Minuman', 24000, 13,  5, TRUE),
('Es Teh Manis',    'Minuman',  8000, 37, 10, TRUE),
('Cokelat Panas',   'Minuman', 20000,  3,  5, TRUE),
('Roti Bakar',      'Makanan', 12000,  7,  5, TRUE),
('Croissant',       'Makanan', 20000,  5,  6, TRUE),
('Nasi Goreng',     'Makanan', 25000,  0,  5, TRUE),
('Kentang Goreng',  'Makanan', 15000, 17,  8, TRUE),
('Brownies',        'Makanan', 18000,  9,  5, TRUE),
('Sandwich',        'Makanan', 22000,  8,  5, TRUE),
('Pisang Goreng',   'Makanan', 10000, 10,  5, FALSE);

-- data penawaran anti-waste
INSERT INTO anti_waste (id_menu, harga_penawaran, batas_waktu, tanggal, aktif) VALUES
(7,   8000, '23:59', CURRENT_DATE,     TRUE),
(8,  15000, '23:59', CURRENT_DATE,     TRUE),
(11, 14000, '10:00', CURRENT_DATE - 1, FALSE);

-- data transaksi penjualan
INSERT INTO transaksi (tanggal, nomor_antrean, nama_pelanggan, total, dibayar, kembalian, status) VALUES
(CURRENT_DATE - 3 + TIME '08:30', 1, 'Budi',   48000,  50000,  2000, 'selesai'),
(CURRENT_DATE - 3 + TIME '10:15', 2, 'Sari',   42000,  50000,  8000, 'selesai'),
(CURRENT_DATE - 3 + TIME '13:40', 3, 'Andi',   66000,  70000,  4000, 'selesai'),
(CURRENT_DATE - 2 + TIME '09:00', 1, 'Dewi',   51000,  51000,     0, 'selesai'),
(CURRENT_DATE - 2 + TIME '11:20', 2, 'Rudi',   46000,  50000,  4000, 'selesai'),
(CURRENT_DATE - 2 + TIME '15:05', 3, 'Maya',   69000,  70000,  1000, 'selesai'),
(CURRENT_DATE - 1 + TIME '08:45', 1, 'Fajar',  58000,  60000,  2000, 'selesai'),
(CURRENT_DATE - 1 + TIME '12:10', 2, 'Lina',   53000,  60000,  7000, 'selesai'),
(CURRENT_DATE - 1 + TIME '16:30', 3, 'Tono',   46000,  50000,  4000, 'selesai'),
(CURRENT_DATE     + TIME '08:20', 1, 'Rina',   62000, 100000, 38000, 'selesai'),
(CURRENT_DATE     + TIME '09:10', 2, 'Hendra', 40000,  40000,     0, 'diproses'),
(CURRENT_DATE     + TIME '09:30', 3, 'Putri',  54000, 100000, 46000, 'diproses');

-- data rincian setiap transaksi
INSERT INTO item_transaksi (id_transaksi, id_menu, jumlah, harga_satuan) VALUES
(1, 1, 2, 18000), (1, 7, 1, 12000),
(2, 3, 1, 22000), (2, 8, 1, 20000),
(3, 9, 2, 25000), (3, 5, 2,  8000),
(4, 2, 1, 15000), (4, 11, 2, 18000),
(5, 4, 1, 24000), (5, 12, 1, 22000),
(6, 1, 3, 18000), (6, 10, 1, 15000),
(7, 1, 1, 18000), (7, 8, 2, 20000),
(8, 9, 1, 25000), (8, 5, 1,  8000), (8, 6, 1, 20000),
(9, 7, 2,  8000), (9, 2, 2, 15000),
(10, 3, 2, 22000), (10, 11, 1, 18000),
(11, 1, 1, 18000), (11, 12, 1, 22000),
(12, 4, 1, 24000), (12, 10, 2, 15000);


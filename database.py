
import psycopg2

HOST = "localhost"
PORT = 5432
NAMA_DB = "CafeCycle"
USER = "postgres"
PASSWORD = "anjaybasda"      # passnya diinput dulu reks


def sambung():
    
    return psycopg2.connect(host=HOST, port=PORT, dbname=NAMA_DB,
                            user=USER, password=PASSWORD)

# ini buat ngambil
def ambil(sql, data=()):
    koneksi = sambung()
    cur = koneksi.cursor()
    cur.execute(sql, data)
    hasil = cur.fetchall()
    cur.close()
    koneksi.close()
    return hasil

# menjalankan beberapa fungsi database
def jalankan(sql, data=()):
    jalankan_banyak([(sql, data)])

# jalanin iterasi beberapa fungsi database sesuai dengan tuplenya 
def jalankan_banyak(daftar):
    koneksi = sambung()
    cur = koneksi.cursor()
    for sql, data in daftar:
        cur.execute(sql, data)
    koneksi.commit()
    cur.close()
    koneksi.close()

# makesure koneksinya dan menginformasikan
def cek_koneksi():
    try:
        sambung().close()
        return True
    except Exception as error:
        print("Gagal terhubung ke database:", error)
        print("Periksa pengaturan di database.py dan pastikan PostgreSQL berjalan.")
        return False


def cek_skema():
    ada = ambil("SELECT table_name, column_name FROM information_schema.columns "
                "WHERE table_name IN ('pengguna', 'menu', 'anti_waste', 'transaksi', 'item_transaksi')")
    perlu = [("pengguna", "username"), ("menu", "stok"), ("item_transaksi", "jumlah"),
             ("transaksi", "dibayar"), ("transaksi", "kembalian"), ("anti_waste", "tanggal")]
    kurang = []
    for tabel, kolom in perlu:
        if (tabel, kolom) not in ada:
            kurang.append(tabel + "." + kolom)

    if len(kurang) > 0:
        print("Struktur database belum lengkap / belum diperbarui. Belum ada:", ", ".join(kurang))
        print("Jalankan file CafeCycle.sql di pgAdmin terlebih dahulu.")
        return False
    return True

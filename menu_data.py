"""Data menu: mengambil menu (beserta harga Anti-Waste), menampilkannya, dan membersihkan deal.

Satu menu = dictionary:
  {"id", "nama", "kategori", "harga", "stok", "harga_jual", "batas"}
  - harga_jual = harga deal kalau ada deal yang masih berlaku, kalau tidak sama dengan harga
  - batas      = jam berakhir deal, atau None kalau tidak ada deal

ATURAN ANTI-WASTE (berdasarkan JAM SISTEM saat ini):
  Sebuah deal otomatis dinonaktifkan (hilang) jika:
    1. jam sistem sudah mencapai batas waktu deal, ATAU
    2. tanggal deal sudah lewat (hari berganti), ATAU
    3. stok menu tersebut habis (0), ATAU
    4. menunya sudah dihapus.
"""
from datetime import datetime
from database import ambil, jalankan
from tampilan import rupiah, input_angka

KATEGORI = ["Makanan", "Minuman"]

SQL_BERSIHKAN = ("UPDATE anti_waste SET aktif = FALSE WHERE aktif = TRUE AND ("
                 " tanggal < %s"
                 " OR (tanggal = %s AND batas_waktu <= %s)"
                 " OR id_menu IN (SELECT id FROM menu WHERE stok <= 0 OR aktif = FALSE))")


def bersihkan_deal(cur=None):
    """Menonaktifkan deal yang sudah habis waktu / stok.

    Tanpa parameter -> berjalan sendiri (koneksi sendiri, langsung commit).
    Dengan cursor   -> ikut transaksi yang sedang berjalan (dipakai saat checkout,
                       supaya pembersihan ini ikut batal kalau checkout gagal)."""
    sekarang = datetime.now()
    data = (sekarang.date(), sekarang.date(), sekarang.time())
    if cur is None:
        jalankan(SQL_BERSIHKAN, data)
    else:
        cur.execute(SQL_BERSIHKAN, data)


def ambil_menu():
    """List menu aktif + stok + deal Anti-Waste yang MASIH berlaku saat ini."""
    bersihkan_deal()
    sekarang = datetime.now()
    baris = ambil("SELECT m.id, m.nama, m.kategori, m.harga, m.stok, a.harga_penawaran, a.batas_waktu "
                  "FROM menu m "
                  "LEFT JOIN anti_waste a ON a.id_menu = m.id AND a.aktif = TRUE "
                  "  AND a.tanggal = %s AND a.batas_waktu > %s "
                  "WHERE m.aktif = TRUE ORDER BY m.id",
                  (sekarang.date(), sekarang.time()))

    daftar = []
    for id_menu, nama, kategori, harga, stok, penawaran, batas in baris:
        harga_jual = harga
        if penawaran is not None:
            harga_jual = penawaran
        daftar.append({"id": id_menu, "nama": nama, "kategori": kategori, "harga": harga,
                       "stok": stok, "harga_jual": harga_jual, "batas": batas})
    return daftar


def cari_menu(id_cari):
    """Satu menu aktif berdasarkan id. Mengembalikan None kalau tidak ada."""
    for menu in ambil_menu():
        if menu["id"] == id_cari:
            return menu
    return None


def minta_menu(teks="ID menu: "):
    """Minta ID menu. Mengembalikan menunya, atau None (dan pesan) kalau tidak ada."""
    menu = cari_menu(input_angka(teks))
    if menu is None:
        print("Menu tidak ditemukan.")
    return menu


def daftar_kategori(daftar):
    """Makanan, Minuman, lalu kategori lain yang ada di data lama (jika ada).
    daftar = list dictionary yang punya kunci \"kategori\"."""
    hasil = list(KATEGORI)
    for item in daftar:
        if item["kategori"] not in hasil:
            hasil.append(item["kategori"])
    return hasil


def judul_kategori(kategori):
    print("=" * 50)
    print(" " + kategori.upper())
    print("-" * 50)


def tampil_menu():
    """Menampilkan menu dibagi per kategori: MAKANAN lalu MINUMAN."""
    daftar = ambil_menu()
    for kategori in daftar_kategori(daftar):
        judul_kategori(kategori)
        ada = False
        for menu in daftar:
            if menu["kategori"] == kategori:
                teks_harga = rupiah(menu["harga"])
                if menu["batas"] is not None:       # ada Anti-Waste Deal yang masih berlaku
                    teks_harga = (rupiah(menu["harga_jual"]) + " (normal " + rupiah(menu["harga"])
                                  + ") DEAL s/d " + str(menu["batas"])[:5])
                teks_stok = "stok " + str(menu["stok"]) if menu["stok"] > 0 else "HABIS"
                print(f"  [{menu['id']}] {menu['nama']} - {teks_harga} - {teks_stok}")
                ada = True
        if not ada:
            print("  (belum ada menu)")
    print("=" * 50)


def pilih_kategori(boleh_kosong=False):
    """Pilih Makanan / Minuman. Mengembalikan nama kategori
    (atau teks kosong jika boleh_kosong dan dikosongkan)."""
    while True:
        print("Kategori: 1. Makanan   2. Minuman")
        akhiran = " (kosongkan = semua): " if boleh_kosong else ": "
        pilihan = input("Pilih kategori" + akhiran).strip()
        if pilihan == "1":
            return KATEGORI[0]
        elif pilihan == "2":
            return KATEGORI[1]
        elif pilihan == "" and boleh_kosong:
            return ""
        print("Pilihan harus 1 atau 2.")

"""Anti-Waste Deals.

- Harga penawaran harus LEBIH RENDAH dari harga normal.
- Deal berlaku HARI INI sampai jam yang ditentukan (dibandingkan dengan jam sistem).
- Jam batas harus LEBIH LAMBAT dari jam sistem saat ini.
- Menu yang stoknya habis tidak bisa diberi deal.
- Deal otomatis hilang saat jam sistem mencapai batas waktu, hari berganti,
  stok menu habis, atau menu dihapus (lihat bersihkan_deal di menu_data.py).
"""
from datetime import datetime, time
from database import ambil, jalankan, jalankan_banyak
from tampilan import header, rupiah, input_angka, info_tanggal, jeda
from menu_data import tampil_menu, minta_menu, bersihkan_deal


def baca_jam(isi):
    """Teks 'HH:MM' -> objek time. Mengembalikan None jika formatnya salah."""
    bagian = isi.split(":")
    if len(bagian) != 2:
        return None
    for b in bagian:
        if not (b.isascii() and b.isdigit()):
            return None
    jam, menit = int(bagian[0]), int(bagian[1])
    if jam > 23 or menit > 59:
        return None
    return time(jam, menit)


def buat_deal():
    header("Buat Deal")
    info_tanggal()
    tampil_menu()
    menu = minta_menu()
    if menu is None:
        return
    if menu["stok"] <= 0:
        print("Gagal: stok menu habis, deal tidak bisa dibuat.")
        return
    penawaran = input_angka("Harga penawaran: ")
    if penawaran <= 0 or penawaran >= menu["harga"]:
        print("Gagal: harga penawaran harus lebih dari 0 dan lebih rendah dari harga normal.")
        return

    sekarang = datetime.now()
    batas = baca_jam(input("Berlaku sampai jam (HH:MM, hari ini): ").strip())
    if batas is None:
        print("Format jam salah. Contoh: 21:30")
        return
    if batas <= sekarang.time():
        print("Gagal: jam harus lebih dari jam sistem saat ini.")
        return

    # deal lama menu yang sama dinonaktifkan, deal baru dibuat untuk HARI INI
    jalankan_banyak([
        ("UPDATE anti_waste SET aktif = FALSE WHERE id_menu = %s", (menu["id"],)),
        ("INSERT INTO anti_waste (id_menu, harga_penawaran, batas_waktu, tanggal) "
         "VALUES (%s, %s, %s, %s)", (menu["id"], penawaran, batas, sekarang.date()))])
    print("Deal dibuat, berlaku sampai", batas.strftime("%H:%M"), "hari ini.")


def nonaktifkan_deal():
    id_deal = input_angka("ID deal: ")
    bersihkan_deal()
    if len(ambil("SELECT id FROM anti_waste WHERE id = %s AND aktif = TRUE", (id_deal,))) == 0:
        print("ID deal tidak ada dalam daftar deal aktif.")
        return
    jalankan("UPDATE anti_waste SET aktif = FALSE WHERE id = %s", (id_deal,))
    print("Deal dinonaktifkan.")


def tampil_deal():
    """Daftar deal yang sedang aktif (deal kedaluwarsa dibersihkan dulu)."""
    bersihkan_deal()
    info_tanggal()
    data = ambil("SELECT a.id, m.nama, m.harga, a.harga_penawaran, a.batas_waktu, m.stok "
                 "FROM anti_waste a JOIN menu m ON m.id = a.id_menu "
                 "WHERE a.aktif = TRUE ORDER BY a.id")
    print("Deal aktif (hilang otomatis saat jam habis atau stok habis):")
    for id_deal, nama, harga, penawaran, batas, stok in data:
        print(f"[{id_deal}] {nama}: {rupiah(harga)} -> {rupiah(penawaran)} "
              f"s/d {str(batas)[:5]} (stok {stok})")
    if len(data) == 0:
        print("(belum ada)")


def menu_anti_waste():
    while True:
        header("Anti-Waste Deals")
        tampil_deal()
        print("1. Buat deal")
        print("2. Nonaktifkan deal")
        print("0. Kembali")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                buat_deal()
                jeda()
            case "2":
                nonaktifkan_deal()
                jeda()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()

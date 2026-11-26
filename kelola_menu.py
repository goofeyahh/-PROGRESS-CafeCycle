# """Kelola menu (tambah, ubah, hapus).
# "Hapus" hanya menyembunyikan menu (aktif = FALSE) supaya riwayat transaksi lama tetap aman."""
from database import jalankan, jalankan_banyak
from tampilan import header, input_angka, jeda
from menu_data import tampil_menu, pilih_kategori, minta_menu


def tambah_menu():
    header("Tambah Menu")
    nama = input("Nama menu: ").strip()
    if nama == "" or len(nama) > 64:
        print("Nama menu wajib diisi, maksimal 64 karakter.")
        return
    kategori = pilih_kategori()
    harga = input_angka("Harga: ")
    if harga <= 0:
        print("Harga harus lebih dari 0.")
        return
    stok = input_angka("Jumlah porsi awal: ")
    jalankan("INSERT INTO menu (nama, kategori, harga, stok) VALUES (%s, %s, %s, %s)",
             (nama, kategori, harga, stok))
    print("Menu ditambahkan.")


def ubah_menu():
    header("Ubah Menu")
    tampil_menu()
    menu = minta_menu("ID menu yang diubah: ")
    if menu is None:
        return
    nama = input("Nama baru (kosongkan jika tetap): ").strip()
    harga = input("Harga baru (kosongkan jika tetap): ").strip()
    ganti_kategori = input("Ubah kategori? (y/n): ").strip().lower()
    if len(nama) > 64:
        print("Nama menu maksimal 64 karakter.")
        return

    # nilai akhir: pakai yang baru jika diisi, kalau tidak pakai yang lama
    nama_akhir = nama if nama != "" else menu["nama"]
    harga_akhir = menu["harga"]
    if harga.isascii() and harga.isdigit() and int(harga) > 0:
        harga_akhir = int(harga)
    kategori_akhir = pilih_kategori() if ganti_kategori == "y" else menu["kategori"]

    jalankan_banyak([
        ("UPDATE menu SET nama = %s, kategori = %s, harga = %s WHERE id = %s",
         (nama_akhir, kategori_akhir, harga_akhir, menu["id"])),
        # deal yang harganya tidak lagi lebih murah dari harga baru ikut dinonaktifkan
        ("UPDATE anti_waste SET aktif = FALSE WHERE id_menu = %s AND harga_penawaran >= %s",
         (menu["id"], harga_akhir))])
    print("Menu diperbarui.")


def hapus_menu():
    header("Hapus Menu")
    tampil_menu()
    menu = minta_menu("ID menu yang dihapus: ")
    if menu is None:
        return
    if input("Hapus menu " + menu["nama"] + "? (y/n): ").strip().lower() == "y":
        jalankan_banyak([
            ("UPDATE menu SET aktif = FALSE WHERE id = %s", (menu["id"],)),
            ("UPDATE anti_waste SET aktif = FALSE WHERE id_menu = %s", (menu["id"],))])
        print("Menu dihapus.")
    else:
        print("Dibatalkan.")


def menu_kelola_menu():
    while True:
        header("Kelola Menu")
        tampil_menu()
        print("1. Tambah menu")
        print("2. Ubah menu")
        print("3. Hapus menu")
        print("0. Kembali")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                tambah_menu()
                jeda()
            case "2":
                ubah_menu()
                jeda()
            case "3":
                hapus_menu()
                jeda()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()

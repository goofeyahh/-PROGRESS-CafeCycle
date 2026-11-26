"""CAFECYCLE - FILE UTAMA.  Jalankan dengan:  python main.py"""
from database import cek_koneksi, cek_skema
from tampilan import header, jeda
from login import login
from pemesanan import pesan
from menu_utama import menu_admin, menu_karyawan


def masuk_pengelola():
    # menindaklanjuti fungsi peran
    peran = login()
    if peran == "admin":
        menu_admin()
    elif peran == "karyawan":
        menu_karyawan()


def menu_awal():
    """Satu kali tampilan menu awal. Mengembalikan True jika pengguna memilih keluar."""
    header("Selamat Datang")
    print("1. Pesan sebagai pelanggan (tanpa login)")
    print("2. Masuk sebagai pengelola (admin / karyawan)")
    print("0. Keluar aplikasi")
    pilihan = input("Pilihan: ").strip()

    match pilihan:
        case "1":
            pesan(False)
        case "2":
            masuk_pengelola()
        case "0":
            return True
        case _:
            print("Pilihan tidak valid.")
            jeda()
    return False


def main():
    if not cek_koneksi() or not cek_skema():
        return

    keluar = False
    while not keluar:
        try:
            keluar = menu_awal()
        except (KeyboardInterrupt, EOFError):       # Ctrl+C di mana pun -> berhenti rapi
            print("\nProgram dihentikan.")
            return
        except Exception as error:                  # mis. database putus -> kembali ke menu awal
            print("Terjadi kesalahan:", error)
            jeda()
    print("Terima kasih!")


main()

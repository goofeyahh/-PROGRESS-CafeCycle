# menu karyawan dan atmin
from tampilan import header, jeda
from pemesanan import pesan
from pesanan_pelanggan import kelola_pesanan
from kelola_menu import menu_kelola_menu
from rekomendasi import rekomendasi_menu
from anti_waste import menu_anti_waste
from kelola_stok import menu_kelola_stok
from riwayat import riwayat_transaksi
from laporan import laporan_penjualan
from pengguna import menu_kredensial, data_karyawan


def menu_karyawan():
    while True:
        header("Menu Karyawan")
        print("1. Pemesanan (kasir)")
        print("2. Pesanan pelanggan")
        print("3. Kelola menu")
        print("4. Rekomendasi menu")
        print("5. Anti-Waste Deals")
        print("6. Kelola stok menu")
        print("7. Riwayat transaksi")
        print("8. Laporan penjualan")
        print("0. Keluar (log out)")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                pesan(True)
            case "2":
                kelola_pesanan()
            case "3":
                menu_kelola_menu()
            case "4":
                rekomendasi_menu()
            case "5":
                menu_anti_waste()
            case "6":
                menu_kelola_stok()
            case "7":
                riwayat_transaksi()
            case "8":
                laporan_penjualan()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()


def menu_admin():
    while True:
        header("Menu Admin")
        print("1. Kelola kredensial")
        print("2. Riwayat pemesanan")
        print("3. Data karyawan")
        print("0. Keluar (log out)")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                menu_kredensial()
            case "2":
                riwayat_transaksi()
            case "3":
                data_karyawan()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()

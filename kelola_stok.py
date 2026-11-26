"""Kelola stok MENU: sisa porsi tiap menu (bukan komposisi/bahan).
Menu dikelompokkan Makanan dan Minuman. Sisa porsi di bawah batas minimum
diberi tanda [!] RENDAH berwarna merah."""
from database import ambil, jalankan
from tampilan import header, input_angka, jeda, MERAH, NORMAL
from menu_data import daftar_kategori, judul_kategori, minta_menu, bersihkan_deal


def tampil_stok():
    """Menampilkan sisa porsi per menu, dibagi per kategori."""
    daftar = []
    for id_menu, nama, kategori, stok, batas in ambil(
            "SELECT id, nama, kategori, stok, batas_minimum FROM menu WHERE aktif = TRUE ORDER BY id"):
        daftar.append({"id": id_menu, "nama": nama, "kategori": kategori, "stok": stok, "batas": batas})

    for kategori in daftar_kategori(daftar):
        judul_kategori(kategori)
        ada = False
        for menu in daftar:
            if menu["kategori"] == kategori:
                tanda = ""
                if menu["stok"] == 0:
                    tanda = "  " + MERAH + "[!] RENDAH (HABIS)" + NORMAL
                elif menu["stok"] < menu["batas"]:
                    tanda = "  " + MERAH + "[!] RENDAH" + NORMAL
                print(f"  [{menu['id']}] {menu['nama']}: sisa {menu['stok']} porsi "
                      f"(minimum {menu['batas']}){tanda}")
                ada = True
        if not ada:
            print("  (belum ada menu)")
    print("=" * 50)


def tambah_porsi():
    menu = minta_menu()
    if menu is None:
        return
    jumlah = input_angka("Jumlah porsi tambahan: ")
    if jumlah <= 0:
        print("Jumlah harus lebih dari 0.")
        return
    jalankan("UPDATE menu SET stok = stok + %s WHERE id = %s", (jumlah, menu["id"]))
    print("Porsi bertambah.")


def atur_porsi():
    menu = minta_menu()
    if menu is None:
        return
    jumlah = input_angka("Sisa porsi sebenarnya sekarang: ")
    jalankan("UPDATE menu SET stok = %s WHERE id = %s", (jumlah, menu["id"]))
    bersihkan_deal()        # jika stok diatur jadi 0, deal menu ini ikut hilang
    print("Sisa porsi diperbarui.")


def ubah_batas():
    menu = minta_menu()
    if menu is None:
        return
    batas = input_angka("Batas minimum baru: ")
    jalankan("UPDATE menu SET batas_minimum = %s WHERE id = %s", (batas, menu["id"]))
    print("Batas minimum diubah.")


def menu_kelola_stok():
    while True:
        header("Kelola Stok Menu")
        tampil_stok()
        print("1. Tambah porsi")
        print("2. Atur jumlah sisa porsi")
        print("3. Ubah batas minimum")
        print("0. Kembali")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                tambah_porsi()
                jeda()
            case "2":
                atur_porsi()
                jeda()
            case "3":
                ubah_batas()
                jeda()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()

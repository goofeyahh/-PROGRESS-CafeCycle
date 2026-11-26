"""Rekomendasi menu sesuai kategori dan anggaran (tidak disimpan)."""
from tampilan import header, rupiah, input_angka, jeda
from menu_data import ambil_menu, pilih_kategori


def rekomendasi_menu():
    header("Rekomendasi Menu")
    kategori = pilih_kategori(boleh_kosong=True)
    anggaran = input_angka("Anggaran maksimal (Rp): ")

    header("Rekomendasi Menu")
    print("Menu yang sesuai anggaran", rupiah(anggaran) + ":")
    ada = False
    for menu in ambil_menu():
        cocok_kategori = (kategori == "" or menu["kategori"].lower() == kategori.lower())
        if cocok_kategori and menu["harga_jual"] <= anggaran and menu["stok"] > 0:
            teks_deal = ""
            if menu["batas"] is not None:
                teks_deal = " (DEAL s/d " + str(menu["batas"])[:5] + ")"
            print(f"[{menu['id']}] {menu['nama']} ({menu['kategori']}) - {rupiah(menu['harga_jual'])}{teks_deal}")
            ada = True
    if not ada:
        print("Tidak ada menu yang cocok.")
    jeda()

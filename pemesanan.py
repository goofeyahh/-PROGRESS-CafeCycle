"""Pemesanan (dipakai pelanggan DAN kasir).

ALUR pesan(): isi nama -> pilih menu (keranjang) -> samakan dengan harga/stok terbaru
              -> total tagihan -> masukkan uang bayar -> simpan (checkout)
              -> struk + nomor antrean.

Keranjang = dictionary:  {id_menu: {"nama": ..., "jumlah": ..., "harga": ...}}
Contoh: {1: {"nama": "Kopi Susu", "jumlah": 2, "harga": 18000},
         7: {"nama": "Roti Bakar", "jumlah": 1, "harga": 8000}}
"""
from datetime import datetime
from database import sambung
from tampilan import header, rupiah, input_angka, info_tanggal, jeda
from menu_data import tampil_menu, ambil_menu, cari_menu, bersihkan_deal

SQL_HARGA_SEKARANG = ("SELECT m.harga, a.harga_penawaran FROM menu m "
                      "LEFT JOIN anti_waste a ON a.id_menu = m.id AND a.aktif = TRUE "
                      "  AND a.tanggal = %s AND a.batas_waktu > %s "
                      "WHERE m.id = %s AND m.aktif = TRUE")


# ---------------------------------------------------------------- keranjang
def total_keranjang(keranjang):
    total = 0
    for item in keranjang.values():
        total += item["harga"] * item["jumlah"]
    return total


def cetak_item(keranjang):
    for item in keranjang.values():
        print(f"  {item['nama']} x{item['jumlah']} @{rupiah(item['harga'])} "
              f"= {rupiah(item['jumlah'] * item['harga'])}")


def sinkronkan_keranjang(keranjang):
    """Menyamakan keranjang dengan harga & stok terbaru
    (promo bisa berakhir dan stok bisa habis selama pelanggan memilih)."""
    terbaru = {}
    for menu in ambil_menu():
        terbaru[menu["id"]] = menu

    for id_menu in list(keranjang):
        item = keranjang[id_menu]
        menu = terbaru.get(id_menu)
        if menu is None or menu["stok"] < item["jumlah"]:
            print("! " + item["nama"] + " sudah tidak tersedia dalam jumlah tersebut, dikeluarkan dari keranjang.")
            del keranjang[id_menu]
        elif menu["harga_jual"] != item["harga"]:
            print("! Harga " + item["nama"] + " berubah: " + rupiah(item["harga"])
                  + " -> " + rupiah(menu["harga_jual"]))
            item["harga"] = menu["harga_jual"]


def pilih_menu_ke_keranjang(nama_pelanggan, kasir):
    """Layar pilih menu, berulang sampai ID 0. Mengembalikan keranjang."""
    keranjang = {}
    while True:
        header("Pemesanan Kasir" if kasir else "Pesan Menu")
        info_tanggal()
        print("Pelanggan:", nama_pelanggan)
        print("Keranjang:")
        if len(keranjang) == 0:
            print("  (kosong)")
        for item in keranjang.values():
            print("  -", item["nama"], "x", item["jumlah"])
        tampil_menu()

        id_menu = input_angka("ID menu (0 = selesai memilih): ")
        if id_menu == 0:
            return keranjang

        menu = cari_menu(id_menu)
        if menu is None or menu["stok"] <= 0:
            print("Menu tidak ada / habis.")
            jeda()
            continue

        jumlah = input_angka("Jumlah: ")
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            jeda()
            continue

        sudah_ada = keranjang[id_menu]["jumlah"] if id_menu in keranjang else 0
        if sudah_ada + jumlah > menu["stok"]:
            print("Stok hanya tersisa", menu["stok"])
            jeda()
            continue

        if id_menu in keranjang:
            keranjang[id_menu]["jumlah"] += jumlah
        else:
            keranjang[id_menu] = {"nama": menu["nama"], "jumlah": jumlah, "harga": menu["harga_jual"]}


# ---------------------------------------------------------------- simpan ke database
def cek_harga_dan_total(cur, keranjang, sekarang):
    """Mencocokkan harga tiap item dengan harga database saat ini
    (promo bisa berakhir tepat sebelum bayar). Mengembalikan (pesan_error, total)."""
    total = 0
    for id_menu, item in keranjang.items():
        cur.execute(SQL_HARGA_SEKARANG, (sekarang.date(), sekarang.time(), id_menu))
        baris = cur.fetchone()
        if baris is None:
            return item["nama"] + " sudah tidak tersedia", 0
        harga_normal, harga_deal = baris
        harga_sekarang = harga_deal if harga_deal is not None else harga_normal
        if harga_sekarang != item["harga"]:
            return ("harga " + item["nama"] + " berubah menjadi " + rupiah(harga_sekarang)
                    + " (promo berakhir / berubah), silakan ulangi pesanan"), 0
        total += item["harga"] * item["jumlah"]
    return "", total


def tutup(koneksi, cur, simpan):
    """Mengakhiri satu paket perubahan: simpan (commit) atau batalkan (rollback)."""
    if simpan:
        koneksi.commit()
    else:
        koneksi.rollback()
    cur.close()
    koneksi.close()


def checkout(keranjang, nama_pelanggan, dibayar):
    """Menyimpan pesanan ke database.
    Mengembalikan (pesan_error, hasil).
      Berhasil -> pesan_error = \"\"  , hasil = (id_transaksi, antrean, total, kembalian, waktu)
      Gagal    -> pesan_error = alasan, hasil = None

    Satu pesanan mengubah 3 tabel dan id transaksi dipakai lagi di langkah berikutnya,
    jadi memakai koneksi & cursor sendiri. commit() hanya SEKALI di akhir; kalau ada
    langkah yang gagal, rollback() membatalkan SEMUA perubahan."""
    sekarang = datetime.now()
    koneksi = sambung()
    cur = koneksi.cursor()

    # 1. Bersihkan deal yang sudah habis, lalu cek harga terbaru & uang bayar
    bersihkan_deal(cur)
    pesan_error, total = cek_harga_dan_total(cur, keranjang, sekarang)
    if pesan_error == "" and dibayar < total:
        pesan_error = "uang yang dibayarkan kurang dari total"
    if pesan_error != "":
        tutup(koneksi, cur, False)
        return pesan_error, None
    kembalian = dibayar - total

    # 2. Nomor antrean = urutan pesanan hari ini
    cur.execute("SELECT COALESCE(MAX(nomor_antrean), 0) + 1 FROM transaksi "
                "WHERE tanggal::date = %s", (sekarang.date(),))
    antrean = cur.fetchone()[0]

    # 3. Simpan data pesanan; id-nya dipakai untuk rincian item
    cur.execute("INSERT INTO transaksi (tanggal, nomor_antrean, nama_pelanggan, total, dibayar, kembalian) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (sekarang, antrean, nama_pelanggan, total, dibayar, kembalian))
    id_transaksi = cur.fetchone()[0]

    # 4. Per item: kurangi stok (hanya jika masih cukup) + simpan rincian
    for id_menu, item in keranjang.items():
        cur.execute("UPDATE menu SET stok = stok - %s WHERE id = %s AND stok >= %s",
                    (item["jumlah"], id_menu, item["jumlah"]))
        if cur.rowcount == 0:
            tutup(koneksi, cur, False)
            return "stok " + item["nama"] + " tidak cukup", None
        cur.execute("INSERT INTO item_transaksi (id_transaksi, id_menu, jumlah, harga_satuan) "
                    "VALUES (%s, %s, %s, %s)", (id_transaksi, id_menu, item["jumlah"], item["harga"]))

    # 5. Menu yang stoknya jadi habis -> deal-nya otomatis hilang
    bersihkan_deal(cur)
    tutup(koneksi, cur, True)
    return "", (id_transaksi, antrean, total, kembalian, sekarang)


# ---------------------------------------------------------------- input & struk
def minta_nama():
    """Minta nama pelanggan sampai terisi."""
    while True:
        nama = input("Nama pelanggan: ").strip()
        if nama == "":
            print("Nama pelanggan tidak boleh kosong.")
        elif len(nama) > 100:
            print("Nama pelanggan maksimal 100 karakter.")
        else:
            return nama


def minta_pembayaran(total, kasir):
    """Minta uang bayar sampai cukup. Mengembalikan 0 jika dibatalkan."""
    if kasir:
        teks = "Uang yang dibayarkan pelanggan (Rp, 0 = batalkan pesanan): "
    else:
        teks = "Masukkan jumlah uang yang Anda bayarkan (Rp, 0 = batalkan pesanan): "
    while True:
        dibayar = input_angka(teks)
        if dibayar == 0 or dibayar >= total:
            return dibayar
        print("Uang kurang", rupiah(total - dibayar), "- masukkan jumlah yang cukup.")


def cetak_struk(keranjang, nama_pelanggan, hasil, dibayar):
    id_transaksi, antrean, total, kembalian, waktu = hasil
    header("Struk")
    print("No. Transaksi :", id_transaksi)
    print("Tanggal       :", waktu.strftime("%Y-%m-%d %H:%M"))
    print("Pelanggan     :", nama_pelanggan)
    print("-" * 50)
    cetak_item(keranjang)
    print("-" * 50)
    print("TOTAL         :", rupiah(total))
    print("DIBAYAR       :", rupiah(dibayar))
    print("KEMBALIAN     :", rupiah(kembalian))
    print("-" * 50)
    print("NOMOR ANTREAN :", antrean)


# ---------------------------------------------------------------- alur utama
def pesan(kasir):
    """kasir=True dari menu karyawan, kasir=False dari pelanggan (tanpa login)."""
    header("Pemesanan Kasir" if kasir else "Pesan Menu")
    info_tanggal()
    nama_pelanggan = minta_nama()

    keranjang = pilih_menu_ke_keranjang(nama_pelanggan, kasir)
    if len(keranjang) > 0:
        header("Pembayaran")
        sinkronkan_keranjang(keranjang)         # samakan dengan harga/stok terbaru
    if len(keranjang) == 0:
        print("Keranjang kosong, pesanan dibatalkan.")
        jeda()
        return

    print("Rincian pesanan:")
    cetak_item(keranjang)
    total = total_keranjang(keranjang)
    print("Total tagihan:", rupiah(total))

    dibayar = minta_pembayaran(total, kasir)
    if dibayar == 0:
        print("Pesanan dibatalkan. Stok tidak berubah.")
        jeda()
        return

    pesan_error, hasil = checkout(keranjang, nama_pelanggan, dibayar)
    if pesan_error != "":
        print("Checkout gagal:", pesan_error)
    else:
        cetak_struk(keranjang, nama_pelanggan, hasil, dibayar)
    jeda()

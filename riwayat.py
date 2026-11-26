"""Riwayat transaksi (karyawan dan admin): filter tanggal, lalu lihat rincian lewat ID."""
from datetime import date
from database import ambil
from tampilan import header, rupiah, input_angka, input_tanggal, info_tanggal, jeda


def ambil_daftar(tanggal):
    """Semua transaksi (tanggal None) atau transaksi pada satu tanggal."""
    if tanggal is None:
        return ambil("SELECT id, tanggal, nama_pelanggan, total, status FROM transaksi ORDER BY id DESC")
    return ambil("SELECT id, tanggal, nama_pelanggan, total, status FROM transaksi "
                 "WHERE tanggal::date = %s ORDER BY id DESC", (tanggal,))


def tampil_rincian(id_trx):
    induk = ambil("SELECT tanggal, nomor_antrean, nama_pelanggan, total, dibayar, kembalian, status "
                  "FROM transaksi WHERE id = %s", (id_trx,))
    if len(induk) == 0:
        print("ID transaksi tidak ditemukan.")
        return
    waktu, antrean, nama, total, dibayar, kembalian, status = induk[0]
    print(f"Transaksi {id_trx} | {str(waktu)[:16]} | {nama} | antrean {antrean} | {status}")
    item = ambil("SELECT m.nama, i.jumlah, i.harga_satuan FROM item_transaksi i "
                 "JOIN menu m ON m.id = i.id_menu WHERE i.id_transaksi = %s", (id_trx,))
    for menu, jumlah, harga in item:
        print(f"  - {menu} x{jumlah} @{rupiah(harga)}")
    print("  Total     :", rupiah(total))
    print("  Dibayar   :", rupiah(dibayar))
    print("  Kembalian :", rupiah(kembalian))


def riwayat_transaksi():
    header("Riwayat Transaksi")
    info_tanggal()
    tanggal = input_tanggal("Filter tanggal YYYY-MM-DD (kosongkan = semua): ",
                            maksimal=date.today())

    while True:
        header("Riwayat Transaksi")
        info_tanggal()
        if tanggal is not None:
            print("Filter tanggal:", tanggal.isoformat())
        data = ambil_daftar(tanggal)
        if len(data) == 0:
            print("Tidak ada transaksi.")
            jeda()
            return

        daftar_id = []
        for id_trx, waktu, nama, total, status in data:
            daftar_id.append(id_trx)
            print(f"[{id_trx}] {str(waktu)[:16]} - {nama} - {rupiah(total)} - {status}")

        id_trx = input_angka("ID transaksi untuk rincian (0 = kembali): ")
        if id_trx == 0:
            return
        if id_trx not in daftar_id:
            print("ID transaksi tidak ada dalam daftar di atas.")
            jeda()
            continue
        print()
        tampil_rincian(id_trx)
        jeda()

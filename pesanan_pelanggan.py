"""Pesanan pelanggan (karyawan): melihat pesanan 'diproses' lalu menandainya 'selesai'."""
from database import ambil, jalankan
from tampilan import header, rupiah, input_angka, jeda


def kelola_pesanan():
    header("Pesanan Pelanggan")
    data = ambil("SELECT id, nomor_antrean, nama_pelanggan, total, tanggal FROM transaksi "
                 "WHERE status = 'diproses' ORDER BY id")
    if len(data) == 0:
        print("Tidak ada pesanan yang sedang diproses.")
        jeda()
        return

    daftar_id = []
    for id_trx, antrean, nama, total, waktu in data:
        daftar_id.append(id_trx)
        print(f"[{id_trx}] Antrean {antrean} - {nama} - {rupiah(total)} - {str(waktu)[:16]}")

    id_trx = input_angka("ID transaksi (0 = kembali): ")
    if id_trx == 0:
        return
    if id_trx not in daftar_id:
        print("ID tidak ada dalam daftar pesanan yang diproses.")
        jeda()
        return

    item = ambil("SELECT m.nama, i.jumlah FROM item_transaksi i "
                 "JOIN menu m ON m.id = i.id_menu WHERE i.id_transaksi = %s", (id_trx,))
    for nama, jumlah in item:
        print("  -", nama, "x", jumlah)

    if len(item) > 0 and input("Tandai selesai? (y/n): ").strip().lower() == "y":
        jalankan("UPDATE transaksi SET status = 'selesai' WHERE id = %s", (id_trx,))
        print("Status diubah menjadi selesai.")
    jeda()

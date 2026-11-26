# Laporan penjualan: jumlah transaksi, pendapatan, rincian per hari, dan produk terlaris.

# ALUR: pilih periode (hari ini / 7 hari terakhir / bulan ini / tanggal sendiri)
#  -> laporan tampil -> kembali ke pilihan periode sampai pengguna memilih 0.
# Tanggal awal tidak boleh setelah tanggal akhir, dan tidak boleh melewati hari ini (tanggal sistem).

from datetime import date, timedelta
from database import ambil
from tampilan import header, rupiah, input_tanggal, info_tanggal, format_tanggal, jeda


def tampil_laporan(awal, akhir):
    header("Laporan Penjualan")
    print(f"Periode : {format_tanggal(awal)} ({awal.isoformat()})")
    print(f"     s/d  {format_tanggal(akhir)} ({akhir.isoformat()})")
    print("=" * 50)

    jumlah, pendapatan = ambil("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM transaksi "
                               "WHERE tanggal::date BETWEEN %s AND %s", (awal, akhir))[0]
    if jumlah == 0:
        print("Tidak ada transaksi pada periode ini.")
        return

    print("Jumlah transaksi   :", jumlah)
    print("Total pendapatan   :", rupiah(pendapatan))
    print("Rata-rata/transaksi:", rupiah(int(pendapatan // jumlah)))

    print("Rincian per hari:")
    per_hari = ambil("SELECT tanggal::date, COUNT(*), SUM(total) FROM transaksi "
                     "WHERE tanggal::date BETWEEN %s AND %s "
                     "GROUP BY tanggal::date ORDER BY tanggal::date", (awal, akhir))
    for tgl, n, subtotal in per_hari:
        print(f"  {tgl.isoformat()} ({format_tanggal(tgl)}): {n} transaksi, {rupiah(subtotal)}")

    print("Produk terlaris:")
    terlaris = ambil("SELECT m.nama, SUM(i.jumlah) AS terjual FROM item_transaksi i "
                     "JOIN transaksi t ON t.id = i.id_transaksi "
                     "JOIN menu m ON m.id = i.id_menu "
                     "WHERE t.tanggal::date BETWEEN %s AND %s "
                     "GROUP BY m.id, m.nama ORDER BY terjual DESC, m.nama LIMIT 5", (awal, akhir))
    for nomor, (nama, terjual) in enumerate(terlaris, start=1):
        print(f"  {nomor}. {nama} ({terjual} terjual)")


def lihat(awal, akhir):
    """Tampilkan laporan satu periode lalu tahan layar."""
    tampil_laporan(awal, akhir)
    jeda()


def laporan_hari_ini():
    hari_ini = date.today()
    lihat(hari_ini, hari_ini)


def laporan_7_hari():
    hari_ini = date.today()
    lihat(hari_ini - timedelta(days=6), hari_ini)


def laporan_bulan_ini():
    hari_ini = date.today()
    lihat(hari_ini.replace(day=1), hari_ini)


def laporan_tanggal_sendiri():
    """Minta tanggal awal lalu akhir; ketik 0 untuk batal."""
    hari_ini = date.today()
    awal = input_tanggal("Tanggal awal  (YYYY-MM-DD, 0 = batal): ",
                         wajib=True, maksimal=hari_ini)
    if awal is None:
        return
    akhir = input_tanggal("Tanggal akhir (YYYY-MM-DD, 0 = batal): ",
                          wajib=True, minimal=awal, maksimal=hari_ini,
                          pesan_min="Tanggal akhir tidak boleh sebelum tanggal awal ("
                                    + awal.isoformat() + ").")
    if akhir is not None:
        lihat(awal, akhir)


def laporan_penjualan():
    while True:
        header("Laporan Penjualan")
        info_tanggal()
        print("1. Hari ini")
        print("2. 7 hari terakhir")
        print("3. Bulan ini")
        print("4. Pilih tanggal sendiri")
        print("0. Kembali")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                laporan_hari_ini()
            case "2":
                laporan_7_hari()
            case "3":
                laporan_bulan_ini()
            case "4":
                laporan_tanggal_sendiri()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()

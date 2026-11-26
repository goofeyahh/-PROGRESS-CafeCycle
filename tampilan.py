"""Tampilan terminal: layar, warna, format rupiah/tanggal, dan semua input dari pengguna."""
import os
from datetime import datetime, date
from getpass import getpass

if os.name == "nt":
    os.system("")          # mengaktifkan warna ANSI di terminal Windows

HIJAU = "\033[42;30m"      # latar hijau, tulisan hitam
MERAH = "\033[1;31m"       # tulisan merah tebal
NORMAL = "\033[0m"         # kembali ke warna biasa

NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
NAMA_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember"]


# ---------------------------------------------------------------- layar
def bersihkan():
    os.system("cls" if os.name == "nt" else "clear")


def header(judul):
    """Layar baru: bersihkan layar lalu tampilkan judul dengan latar hijau."""
    bersihkan()
    print(HIJAU + " " * 50 + NORMAL)
    print(HIJAU + ("CAFECYCLE | " + judul).center(50) + NORMAL)
    print(HIJAU + " " * 50 + NORMAL)


def jeda():
    """Menahan layar supaya pesan sempat dibaca."""
    input("\nTekan Enter untuk lanjut...")


# ---------------------------------------------------------------- format
def rupiah(angka):
    """18000 -> Rp18.000"""
    return "Rp" + f"{angka:,}".replace(",", ".")


def format_tanggal(tgl):
    """Contoh: Rabu, 25 November 2026."""
    return f"{NAMA_HARI[tgl.weekday()]}, {tgl.day} {NAMA_BULAN[tgl.month - 1]} {tgl.year}"


def info_tanggal():
    """Tanggal dan jam SISTEM saat ini."""
    sekarang = datetime.now()
    print(f"Tanggal sistem hari ini : {format_tanggal(sekarang)} ({sekarang:%Y-%m-%d})")
    print(f"Jam sistem sekarang     : {sekarang:%H:%M:%S}")


# ---------------------------------------------------------------- input
def input_angka(teks):
    """Minta input sampai berupa angka bulat (0 atau lebih)."""
    while True:
        isi = input(teks).strip()
        if isi.isascii() and isi.isdigit():
            return int(isi)
        print("Harus berupa angka!")


def hari_dalam_bulan(tahun, bulan):
    """Jumlah hari pada bulan tersebut (februari mengikuti tahun kabisat)."""
    hari = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    kabisat = (tahun % 4 == 0 and tahun % 100 != 0) or tahun % 400 == 0
    if bulan == 2 and kabisat:
        return 29
    return hari[bulan - 1]


def baca_tanggal(isi):
    """Teks 'YYYY-MM-DD' -> objek date. Mengembalikan None jika format salah
    atau tanggalnya tidak ada (misalnya 2026-02-30)."""
    bagian = isi.split("-")
    if len(bagian) != 3:
        return None
    for b in bagian:
        if not (b.isascii() and b.isdigit()):
            return None
    tahun, bulan, hari = int(bagian[0]), int(bagian[1]), int(bagian[2])
    if len(bagian[0]) != 4 or tahun < 1000:
        return None
    if bulan < 1 or bulan > 12:
        return None
    if hari < 1 or hari > hari_dalam_bulan(tahun, bulan):
        return None
    return date(tahun, bulan, hari)


def input_tanggal(teks, wajib=False, minimal=None, maksimal=None, pesan_min=None):
    """Minta tanggal format YYYY-MM-DD, mengembalikan objek date.

    wajib=False : dikosongkan -> mengembalikan None.
    wajib=True  : tidak boleh kosong; ketik 0 untuk batal -> mengembalikan None.
    minimal / maksimal : batas tanggal yang boleh (objek date).
    """
    while True:
        isi = input(teks).strip()
        if isi == "":
            if not wajib:
                return None
            print("Tanggal wajib diisi (0 = batal).")
            continue
        if wajib and isi == "0":
            return None

        tgl = baca_tanggal(isi)
        if tgl is None:
            print("Format harus YYYY-MM-DD dan tanggalnya harus ada, contoh:", date.today().isoformat())
        elif maksimal is not None and tgl > maksimal:
            print(f"Tanggal tidak boleh setelah {maksimal.isoformat()}.")
        elif minimal is not None and tgl < minimal:
            print(pesan_min if pesan_min is not None else f"Tanggal tidak boleh sebelum {minimal.isoformat()}.")
        else:
            return tgl


def input_password(teks):
    """Input password: setiap huruf yang diketik tampil sebagai bintang (*).
    Di Windows dibaca tombol demi tombol; di sistem lain memakai getpass (tidak tampil)."""
    if os.name != "nt":
        return getpass(teks)

    import msvcrt
    print(teks, end="", flush=True)
    hasil = ""
    while True:
        tombol = msvcrt.getwch()
        if tombol == "\r" or tombol == "\n":        # Enter
            print()
            return hasil
        elif tombol == "\003":                      # Ctrl+C
            raise KeyboardInterrupt
        elif tombol == "\b":                        # Backspace
            if hasil != "":
                hasil = hasil[:-1]
                print("\b \b", end="", flush=True)
        elif tombol == "\x00" or tombol == "\xe0":  # tombol khusus (panah, F1, dll.) diabaikan
            msvcrt.getwch()
        else:
            hasil += tombol
            print("*", end="", flush=True)

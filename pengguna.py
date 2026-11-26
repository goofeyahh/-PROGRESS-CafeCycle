# kelola pengguna (khusus admin): buat/hapus akun karyawan dan lihat daftar karyawan.
# password yang diketik tampil sebagai bintang.
from database import ambil, jalankan
from tampilan import header, input_password, jeda


def buat_akun():
    header("Buat Akun Karyawan")
    username = input("Username baru: ").strip()
    password = input_password("Password: ")
    if username == "" or password == "":
        print("Username dan password tidak boleh kosong.")
    elif len(username) > 50 or len(password) > 50:
        print("Username dan password maksimal 50 karakter.")
    elif len(ambil("SELECT id FROM pengguna WHERE username = %s", (username,))) > 0:
        print("Username sudah dipakai.")
    elif input_password("Ulangi password: ") != password:
        print("Password tidak sama, akun tidak dibuat.")
    else:
        jalankan("INSERT INTO pengguna (username, password, peran) VALUES (%s, %s, 'karyawan')",
                 (username, password))
        print("Akun karyawan dibuat.")


def hapus_akun():
    header("Hapus Akun Karyawan")
    username = input("Username yang dihapus: ").strip()
    ada = ambil("SELECT id FROM pengguna WHERE username = %s AND peran = 'karyawan'", (username,))
    if len(ada) == 0:
        print("Akun karyawan tidak ditemukan.")
    else:
        jalankan("DELETE FROM pengguna WHERE username = %s AND peran = 'karyawan'", (username,))
        print("Akun dihapus.")


def menu_kredensial():
    while True:
        header("Kelola Kredensial")
        print("1. Buat akun karyawan")
        print("2. Hapus akun karyawan")
        print("0. Kembali")
        pilihan = input("Pilihan: ").strip()

        match pilihan:
            case "1":
                buat_akun()
                jeda()
            case "2":
                hapus_akun()
                jeda()
            case "0":
                break
            case _:
                print("Pilihan tidak valid.")
                jeda()


def data_karyawan():
    header("Data Karyawan")
    for username, password in ambil("SELECT username, password FROM pengguna WHERE peran = 'karyawan'"):
        print(f"  - {username} (password: {password})")
    jeda()

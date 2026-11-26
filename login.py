# login admin / karyawan. 
# password tampil sebagai bintang.
from database import ambil
from tampilan import header, input_password, jeda


def login():
    # makesure percobaan cuman 3x dan kalo gagal maka akan ksosong outputnya
    header("Login")
    for percobaan in range(1, 4):
        username = input("Username: ").strip()
        password = input_password("Password: ")
        hasil = ambil("SELECT peran FROM pengguna WHERE username = %s AND password = %s",
                      (username, password))
        if len(hasil) > 0:
            return hasil[0][0]
        print(f"Username atau password salah ({percobaan} / 3)")
    print("Percobaan login habis.")
    jeda()
    return ""

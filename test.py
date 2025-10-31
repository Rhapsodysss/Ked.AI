# Fungsi untuk penambahan
def tambah(angka1, angka2):
    return angka1 + angka2

# Fungsi untuk pengurangan


def kurang(angka1, angka2):
    return angka1 - angka2

# Fungsi untuk perkalian


def perkalian(angka1, angka2):
    return angka1 * angka2

# Fungsi untuk pembagian


def bagi(angka1, angka2):
    # Hindari pembagian dengan nol
    if angka2 == 0:
        return "Error: Tidak bisa membagi dengan nol!"
    return angka1 / angka2


def kalkulator():
    print("Selamat datang di Kalkulator Sederhana!")
    print("Pilih operasi:")
    print("1. Tambah")
    print("2. Kurang")
    print("3. Kali")
    print("4. Bagi")

    # Minta input dari pengguna
    while True:
        pilihan = input("Masukkan pilihan (1/2/3/4): ")

        # Cek apakah pilihan valid
        if pilihan in ('1', '2', '3', '4'):
            try:
                # Meminta input angka pertama
                num1 = float(input("Masukkan angka pertama: "))
                # Meminta input angka kedua
                num2 = float(input("Masukkan angka kedua: "))
            except ValueError:
                print("Input tidak valid. Mohon masukkan angka.")
                continue

            if pilihan == '1':
                hasil = tambah(num1, num2)
                operasi = '+'
            elif pilihan == '2':
                hasil = kurang(num1, num2)
                operasi = '-'
            elif pilihan == '3':
                hasil = perkalian(num1, num2)
                operasi = '*'
            elif pilihan == '4':
                hasil = bagi(num1, num2)
                operasi = '/'

            # Menampilkan hasil
            print(f"{num1} {operasi} {num2} = {hasil}")

            # Keluar dari loop setelah perhitungan
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


# Memanggil fungsi utama kalkulator untuk menjalankan program
if __name__ == "__main__":
    kalkulator()

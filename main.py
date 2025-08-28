import cv2
import numpy as np
import mss
import pydirectinput
import time

# --- Variabel Konfigurasi ---
# Sesuaikan ini dengan judul jendela Brawlhalla Anda
BRAWLHALLA_WINDOW_TITLE = "Brawlhalla" 
# Sesuaikan dengan resolusi monitor Anda
# Untuk sementara kita tangkap seluruh layar
MONITOR_CONFIG = {"top": 0, "left": 0, "width": 1920, "height": 1080}

# Muat gambar template kita
try:
    # --- PERUBAHAN DI SINI ---
    # Muat template langsung sebagai Grayscale agar formatnya sama dengan screen_gray
    player_template = cv2.imread('assets/player_template.png', cv2.IMREAD_GRAYSCALE)
    enemy_template = cv2.imread('assets/enemy_template.png', cv2.IMREAD_GRAYSCALE)
    attack_template = cv2.imread('assets/dodge.png', cv2.IMREAD_GRAYSCALE)

    # Menambahkan pengecekan jika file tidak berhasil dimuat
    if player_template is None or enemy_template is None or attack_template is None:
        raise IOError("Salah satu file template tidak ditemukan atau tidak bisa dibaca. Cek kembali path dan nama file.")

    # Dapatkan dimensi dari template untuk menggambar kotak nanti
    h_player, w_player = player_template.shape[:2]
    h_enemy, w_enemy = enemy_template.shape[:2]
    h_attack, w_attack = attack_template.shape[:2]
except Exception as e:
    print(f"Error: Gagal memuat gambar template. Detail: {e}")
    exit()

# SCTE (Screencast Tool) object untuk menangkap layar
sct = mss.mss()

def find_object(screen, template, threshold=0.7):
    """
    Fungsi untuk mencari posisi sebuah objek (template) di dalam layar (screen).
    Mengembalikan koordinat tengah objek jika ditemukan, jika tidak None.
    """
    # Mencocokkan template dengan layar
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    
    # Dapatkan lokasi dengan kecocokan tertinggi
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        # Jika kecocokan lebih tinggi dari threshold, kita anggap objek ditemukan
        # max_loc adalah pojok kiri atas, kita hitung tengahnya
        center_x = max_loc[0] + template.shape[1] // 2
        center_y = max_loc[1] + template.shape[0] // 2
        return (center_x, center_y), max_loc, max_val
    return None, None, None

print("Bot akan dimulai dalam 3 detik. Pindah ke jendela Brawlhalla...")
time.sleep(3)
print("Bot Aktif! Tekan 'q' pada jendela debug untuk keluar.")

# Jarak aman yang diinginkan dari musuh (dalam pixel)
SAFE_DISTANCE = 250 

# --- GANTI SELURUH LOOP 'while True' ANDA DENGAN INI ---
while True:
    # 1. PERSEPSI (Melihat Layar)
    screen_raw = sct.grab(MONITOR_CONFIG)
    screen_img = np.array(screen_raw)
    # Kita butuh gambar berwarna untuk menggambar kotak, jadi kita simpan
    # Lalu kita buat versi grayscale untuk deteksi
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)

    # 2. ANALISIS (Mencari Player, Musuh, dan Serangan)
    player_pos, player_top_left, player_score = find_object(screen_gray, player_template, threshold=0.5) # Threshold diturunkan untuk debug
    enemy_pos, enemy_top_left, enemy_score = find_object(screen_gray, enemy_template, threshold=0.5)
    attack_pos, attack_top_left, attack_score = find_object(screen_gray, attack_template, threshold=0.4)

    # Cetak skor tertinggi yang ditemukan di setiap frame untuk debug
    # Ini akan membantu kita tahu seberapa dekat kecocokannya
    print(f"Skor Player: {player_score:.2f}, Skor Musuh: {enemy_score:.2f}")

    # --- BAGIAN DEBUG VISUAL BARU ---
    if player_pos:
        # Gambar kotak di sekitar player yang terdeteksi
        cv2.rectangle(screen_img, player_top_left, (player_top_left[0] + w_player, player_top_left[1] + h_player), (0, 255, 0), 2)
        cv2.putText(screen_img, f"Player: {player_score:.2f}", (player_top_left[0], player_top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if enemy_pos:
        # Gambar kotak di sekitar musuh yang terdeteksi
        cv2.rectangle(screen_img, enemy_top_left, (enemy_top_left[0] + w_enemy, enemy_top_left[1] + h_enemy), (0, 0, 255), 2)
        cv2.putText(screen_img, f"Musuh: {enemy_score:.2f}", (enemy_top_left[0], enemy_top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # --- AKHIR BAGIAN DEBUG VISUAL ---

    # 3. LOGIKA & AKSI (Sementara kita nonaktifkan agar fokus pada deteksi)
    # (Anda bisa menghapus komentar di bawah ini setelah deteksi berhasil)
    # if player_pos and enemy_pos:
    #     # ... (logika dodge dan spacing ada di sini) ...
    #     pass # Sementara tidak melakukan apa-apa

    # Tampilkan jendela debug
    cv2.imshow('Jendela Debug Bot', screen_img)

    # Cek jika tombol 'q' ditekan untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Hancurkan semua jendela setelah loop selesai
cv2.destroyAllWindows()
print("Bot dihentikan.")
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
# MONITOR_CONFIG = {"top": 0, "left": 0, "width": 1920, "height": 1080}
# (Angka ini cocok untuk monitor 1080p, bisa disesuaikan)
MONITOR_CONFIG = {"top": 200, "left": 300, "width": 1320, "height": 600}

# Muat gambar template kita
try:
    player_template = cv2.imread('assets/player_template.png', cv2.IMREAD_GRAYSCALE)
    enemy_template = cv2.imread('assets/enemy_template.png', cv2.IMREAD_GRAYSCALE)
    attack_template = cv2.imread('assets/dodge.png', cv2.IMREAD_GRAYSCALE)

    if player_template is None or enemy_template is None or attack_template is None:
        raise IOError("Salah satu file template tidak ditemukan. Cek path dan nama file.")

    h_player, w_player = player_template.shape[:2]
    h_enemy, w_enemy = enemy_template.shape[:2]
    h_attack, w_attack = attack_template.shape[:2]

    # --- KODE PENGAMAN BARU ---
    # Cek apakah ada template yang lebih besar dari area monitor
    if h_player > MONITOR_CONFIG['height'] or w_player > MONITOR_CONFIG['width']:
        raise ValueError("Ukuran 'player_template.png' lebih besar dari area monitor. Harap crop gambarnya!")
    if h_enemy > MONITOR_CONFIG['height'] or w_enemy > MONITOR_CONFIG['width']:
        raise ValueError("Ukuran 'enemy_template.png' lebih besar dari area monitor. Harap crop gambarnya!")
    if h_attack > MONITOR_CONFIG['height'] or w_attack > MONITOR_CONFIG['width']:
        raise ValueError("Ukuran 'dodge.png' lebih besar dari area monitor. Harap crop gambarnya!")
    # --- AKHIR KODE PENGAMAN ---

except Exception as e:
    print(f"Error: Gagal memuat atau memvalidasi gambar template. Detail: {e}")
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

SAFE_DISTANCE = 250 

while True:
    screen_raw = sct.grab(MONITOR_CONFIG)
    screen_img = np.array(screen_raw)
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)

    player_pos, player_top_left, player_score = find_object(screen_gray, player_template, threshold=0.55) # Threshold bisa sedikit dinaikkan
    enemy_pos, enemy_top_left, enemy_score = find_object(screen_gray, enemy_template, threshold=0.55)
    attack_pos, attack_top_left, attack_score = find_object(screen_gray, attack_template, threshold=0.4)

    # --- PERBAIKAN UTAMA ADA DI SINI ---
    # Sebelum mencetak, kita cek dulu apakah skornya ada (bukan None)
    # Jika None, kita tampilkan "N/A" agar tidak crash.
    player_score_str = f"{player_score:.2f}" if player_score is not None else "N/A"
    enemy_score_str = f"{enemy_score:.2f}" if enemy_score is not None else "N/A"
    print(f"Skor Player: {player_score_str}, Skor Musuh: {enemy_score_str}")

    # Menggambar kotak hanya jika objek ditemukan
    if player_pos:
        cv2.rectangle(screen_img, player_top_left, (player_top_left[0] + w_player, player_top_left[1] + h_player), (0, 255, 0), 2)
        cv2.putText(screen_img, f"Player: {player_score_str}", (player_top_left[0], player_top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if enemy_pos:
        cv2.rectangle(screen_img, enemy_top_left, (enemy_top_left[0] + w_enemy, enemy_top_left[1] + h_enemy), (0, 0, 255), 2)
        cv2.putText(screen_img, f"Musuh: {enemy_score_str}", (enemy_top_left[0], enemy_top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Sekarang kita aktifkan kembali Logika & Aksi
    if player_pos and enemy_pos:
        # Prioritaskan Dodge
        is_attack_near = False
        if attack_pos:
            distance_to_attack = np.sqrt((attack_pos[0] - player_pos[0])**2 + (attack_pos[1] - player_pos[1])**2)
            if distance_to_attack < 150:
                is_attack_near = True
        
        if is_attack_near:
            print("SERANGAN TERDETEKSI! DODGE.")
            pydirectinput.press('shift')
            time.sleep(0.5)
        else:
            # Logika Spacing jika tidak ada serangan
            distance_x = player_pos[0] - enemy_pos[0]
            if abs(distance_x) < SAFE_DISTANCE:
                if distance_x > 0: pydirectinput.press('d')
                else: pydirectinput.press('a')

    cv2.imshow('Jendela Debug Bot', screen_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("Bot dihentikan.")



#28-8-2025 => DAY-1: Membangun kerangka dasar bot untuk Brawlhalla, hasilnya tadi sudah bisa menampilkan screen di brawlhallaya cuman masih bug dan perlu perbaikan lebih lanjut serta tadi forclose screenya.
#29-8-2025 => DAY-2: Memperbaiki bug yang ada di kode kemarin, menambahkan logika dasar spacing dan dodge, serta menambahkan validasi gambar template agar tidak lebih besar dari area monitor. KEMUDIAN BOOM ADA PERUBAHAN BESAR BOT SUDAH BISA BERGERAK AT LEAST DENGAN CODEE PYTHON CUMANA TRAKING UNTUK PLAYERNYA MASIH KURANG JADI SERING BERHENTI TIBA TIBAAA DAN TIDAK TER TRAKAING DENGAAN BAIK CUMAN SEHINGA TIDAK MELAKUAN DOUDE DAN JUGA SPASING DENGAN BAIK. NEXT HARUS DI TELEURUSI  MASALAHNYA DAN DI BREIKJN MUNKIN DATASET BERUPA GAMBAR LEBIH BAMYAK LAGIA AGAR BISA TRAKING GAMABAAR PLAYER DAN USUH DI SEGALA KONDISI ANIMASINYA.
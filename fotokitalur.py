import cv2
import mediapipe as mp
import time

acuan = time.time()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Membuka kamera (0 = kamera default)
cap = cv2.VideoCapture(0)

# Cek apakah kamera berhasil dibuka
if not cap.isOpened():
    print("Gagal membuka kamera.")
    exit()

print("Kamera berhasil dibuka.")
print("Tekan tombol 'q' untuk keluar.")
blur_level = 1
while True:
    # Membaca frame dari kamera
    ret, frame = cap.read()

    if not ret:
        print("Gagal membaca frame.")
        break
    
    #Mirror
    frame = cv2.flip(frame, 1)
    #biar bisa dibaca mediapipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    telunjuk_kiri = False
    tengah_kiri = False

    telunjuk_kanan = False
    tengah_kanan = False
    ibu = False
    manis = False
    kelingking = False

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness):

            hand = handedness.classification[0].label #ngasih tau kanan atau kiri

            telunjuk = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y #
            tengah = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
            manis = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y #
            kelingking = hand_landmarks.landmark[20].y < hand_landmarks.landmark[10].y
            ibu = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x

            if hand == "Left":
                telunjuk_kiri = telunjuk
                tengah_kiri = tengah

            elif hand == "Right":
                telunjuk_kanan = telunjuk
                tengah_kanan = tengah


    peace_kiri = telunjuk_kiri and tengah_kiri
    peace_kanan = telunjuk_kanan and tengah_kanan
    konfirm = not(ibu or manis or kelingking)
    now = time.time()
    jeda = now - acuan

    if jeda > 0.1:
        if (peace_kanan and peace_kiri and konfirm):
            print("Foto kita blurrrrrr")
            if blur_level >= 51:
                blur_level += 0
            else:
                blur_level += 2

            blur = cv2.GaussianBlur(frame, (blur_level, blur_level), 0)
        else:
            if blur_level == 1:
                blur_level -= 0
                blur = frame
            elif (blur_level <= 6 and blur_level >= 1):
                blur_level -= 2
                blur = cv2.GaussianBlur(frame, (blur_level, blur_level), 0)
            else:
                blur_level -= 6
                blur = cv2.GaussianBlur(frame, (blur_level, blur_level), 0)

        acuan = now

    # Menampilkan frame
    cv2.imshow("blurrrrrr", blur)

    # Keluar jika tombol q ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Menutup kamera
cap.release()

# Menutup semua jendela OpenCV
cv2.destroyAllWindows()

print("Kamera ditutup.")
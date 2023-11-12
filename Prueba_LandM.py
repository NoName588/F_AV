import mediapipe as mp
import cv2
import socket

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Configuración de los Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

with mp_hands.Hands() as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        height, width, _ = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        landmark_data_list = []

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                hand_1 = landmarks
                landmark_data = []
                for landmark in hand_1.landmark:
                    x = int(landmark.x * width)  # Coordenada x en píxeles (entero)
                    y = int(landmark.y * height)  # Coordenada y en píxeles (entero)
                    z = int(landmark.z * 100)  # Escalar y convertir z en un número entero
                    landmark_data.append([x, y, z])
                landmark_data_list.append(landmark_data)
        # Enviar la lista de forma correcta para Unity
        data_str = ";".join([",".join(map(str, l)) for l in landmark_data_list])
        sock.sendto(data_str.encode(), serverAddressPort)
        print(f"Enviado a través del socket: {data_str}")

        cv2.imshow("Hand Landmarks", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()



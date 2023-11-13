import os
import cv2
import csv
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import HandPoseEmbedder
import Draw_Hand_landmarks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import socket

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)

# For webcam input:
cap = cv2.VideoCapture(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)


def load_pose_samples(pose_samples_folder, file_extension='csv'):
    """ Loads pose samples from a given folder."""

    file_names = [name for name in os.listdir(pose_samples_folder) if name.endswith(file_extension)]

    pose_samples = []
    class_samples = []
    for file_name in file_names:
        class_name = file_name[:-(len(file_extension) + 1)]

        # Parse CSV
        with open(os.path.join(pose_samples_folder, file_name)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                landmarks = np.array(row[:], np.float32).reshape(21, 2)
                landmarks = landmarks[:, :2].reshape((42,))
                pose_samples.append(landmarks)
                class_samples.append(class_name)
    return pose_samples, class_samples


# Function to get hand landmarks from a frame and draw them
def process_frame(frame):
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        # Limit to one hand detection
        landmarks = results.multi_hand_landmarks[0].landmark
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        return landmarks
    else:
        return None


data_dir = os.path.dirname(os.path.abspath(__file__))

x, y = load_pose_samples(data_dir)
# print(x, y)
# Draw_Hand_landmarks.plot_random_pose(x, y, np.random.randint(len(y), size=25))

pose_embedder = HandPoseEmbedder.HandPoseEmbedder()
x_embedding = [pose_embedder(instance) for instance in x]
x_embedding = np.asarray(x_embedding)

X_train, X_test, y_train, y_test = train_test_split(x_embedding, y, random_state=0, test_size=0.2)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(y_train)
y_test = label_encoder.transform(y_test)
print(label_encoder.classes_)

classifier = KNeighborsClassifier(n_neighbors=7)
classifier.fit(X_train, y_train)

plt.figure(figsize=(5, 5))
disp = ConfusionMatrixDisplay.from_estimator(classifier, X_test, y_test, display_labels=label_encoder.classes_,
                                            cmap=plt.cm.Blues, ax=plt.gca())
# plt.show()
print(disp.confusion_matrix)

# Video Capture
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue
    hand_landmarks = process_frame(frame)
    flip = cv2.flip(frame, 1)
    if hand_landmarks is not None:
        # Process the hand landmarks
        landmarks = [lmk for lmk in hand_landmarks]  # Extract all landmarks
        landmarks_array = np.zeros((21, 2), dtype=np.float32)
        for i, lmk in enumerate(landmarks):
            landmarks_array[i] = [lmk.x, lmk.y]
        landmarks_array = landmarks_array.flatten()  # Flatten to a 1D array

        # Print the x and y coordinates of each landmark
        x_coordinates = landmarks_array[::2]
        y_coordinates = landmarks_array[1::2]
        #print("X Coordinates:", x_coordinates)
        #print("Y Coordinates:", y_coordinates)

        # Embed the hand landmarks
        hand_embedding = pose_embedder(landmarks_array)
        # Preprocess the data
        hand_embedding = scaler.transform([hand_embedding])
        # Predict using the classifier
        predicted_class = classifier.predict(hand_embedding)
        # Draw the predicted class on the frame
        
        data_str = f"{predicted_class[0]};{';'.join([','.join(map(str, [lmk.x, lmk.y])) for lmk in landmarks])}"
        sock.sendto(data_str.encode(), serverAddressPort)

        cv2.putText(flip, f'Predicted: {label_encoder.classes_[predicted_class[0]]}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Hands Classifier', flip)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

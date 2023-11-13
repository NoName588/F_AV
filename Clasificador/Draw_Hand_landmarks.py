import math
from typing import List, Tuple, Union
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt


def _normalized_to_pixel_coordinates(normalized_x: float, normalized_y: float, image_width: int, image_height: int) -> (
        Union)[None, Tuple[int, int]]:

  x_px = min(math.floor(normalized_x * image_width), image_width - 1)
  y_px = min(math.floor(normalized_y * image_height), image_height - 1)
  return x_px, y_px


def draw_landmarks(image: np.ndarray, landmarks: np.ndarray, connections: List[Tuple[int, int]] = None):
  """""Draws the landmarks and the connections on the image.
  Args:
    image: A three channel RGB image represented as numpy ndarray.
    landmarks: A normalized landmark numpy array
    connections: A list of landmark index tuples that specifies how landmarks to be connected in the drawing.
  Raises:
    ValueError: If one of the followings:
      a) If the input image is not three channel RGB.
      b) If any connetions contain invalid landmark index.
  """
  if image.shape[2] != 3:
    raise ValueError('Input image must contain three channel rgb data.')
  image_rows, image_cols, _ = image.shape
  idx_to_coordinates = {}
  for idx in range(21):
    landmark_px = _normalized_to_pixel_coordinates(landmarks[2*idx], landmarks[2*idx+1], image_cols, image_rows)
    if landmark_px:
      idx_to_coordinates[idx] = landmark_px
  if connections:
    num_landmarks = 21
    # Draws the connections if the start and end landmarks are both visible.
    for connection in connections:
      start_idx = connection[0]
      end_idx = connection[1]
      if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
        raise ValueError(f'Landmark index is out of range. Invalid connection '
                         f'from landmark #{start_idx} to landmark #{end_idx}.')
      if start_idx in idx_to_coordinates and end_idx in idx_to_coordinates:
        cv2.line(image, idx_to_coordinates[start_idx], idx_to_coordinates[end_idx], (0, 255, 0), 2)

  # Draws landmark points after finishing the connection lines, which is aesthetically better.
  for landmark_px in idx_to_coordinates.values():
    cv2.circle(image, landmark_px, 2, (255, 0, 0), 2)


hand_connections = mp.solutions.hands.HAND_CONNECTIONS


def plot_random_pose(features, labels, indexes):
  plt.figure(figsize=(10, 10))
  for i in range(25):
    img = np.zeros((200, 200, 3), dtype = "uint8")
    plt.subplot(5, 5, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    hand_landmarks = features[indexes[i]]
    draw_landmarks(img, hand_landmarks, hand_connections)
    plt.imshow(img)
    plt.xlabel(labels[indexes[i]])
  plt.show()

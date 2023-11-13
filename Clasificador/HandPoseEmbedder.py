import numpy as np


class HandPoseEmbedder(object):
    """Converts 2D pose landmarks into 2D embedding."""

    def __init__(self):
        # Names of the landmarks as they appear in the prediction.
        self._landmark_names = [
            'WRIST',
            'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
            'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
            'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
            'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
            'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP',
        ]

    def __call__(self, landmarks):
        """Converts pose landmarks to embedding

        Args:
          landmarks - NumPy array with 2D landmarks of shape (42,).

        Result:
          Numpy array with pose embedding of shape (M, 2) where M is the number of
          pairwise distances defined in `_get_pose_distance_embedding`.
        """

        landmarks = landmarks.reshape(21, 2)                                     # Get pose landmarks as 2D points
        embedding = self._get_pose_distance_embedding(landmarks)                # Get embedding....
        return embedding.flatten()                                              # as a row vector

    def _get_pose_distance_embedding(self, landmarks):
        """Converts pose landmarks into 2D embedding.

        Usamos varias distancias 2D por pares para formar l embedding.
        Todas las distancias incluyen componentes X e Y con signo.
        Usamos diferentes tipos de pares para cubrir diferentes clases de pose.
        Siéntase libre de eliminar algunos o agregar nuevos.

        Args:
          landmarks - NumPy array with 2D landmarks of shape (N, 2).

        Result:
          Numpy array with pose embedding of shape (M, 1) where M is the number of
          pairwise distances.
        """
        embedding = np.array([
            # One joint.
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'THUMB_MCP'),
            self._get_distance_by_names(landmarks, 'INDEX_FINGER_TIP', 'INDEX_FINGER_MCP'),
            self._get_distance_by_names(landmarks, 'MIDDLE_FINGER_TIP', 'MIDDLE_FINGER_MCP'),
            self._get_distance_by_names(landmarks, 'RING_FINGER_TIP', 'RING_FINGER_MCP'),
            self._get_distance_by_names(landmarks, 'PINKY_TIP', 'PINKY_MCP'),

            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'THUMB_IP'),
            self._get_distance_by_names(landmarks, 'INDEX_FINGER_TIP', 'INDEX_FINGER_PIP'),
            self._get_distance_by_names(landmarks, 'MIDDLE_FINGER_TIP', 'MIDDLE_FINGER_PIP'),
            self._get_distance_by_names(landmarks, 'RING_FINGER_TIP', 'RING_FINGER_PIP'),
            self._get_distance_by_names(landmarks, 'PINKY_TIP', 'PINKY_PIP'),

            # Two joints.
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'INDEX_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'MIDDLE_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'RING_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'PINKY_TIP'),

            self._get_distance_by_names(landmarks, 'INDEX_FINGER_TIP', 'MIDDLE_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'INDEX_FINGER_TIP', 'RING_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'INDEX_FINGER_TIP', 'PINKY_TIP'),

            self._get_distance_by_names(landmarks, 'MIDDLE_FINGER_TIP', 'RING_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'MIDDLE_FINGER_TIP', 'PINKY_TIP'),

            self._get_distance_by_names(landmarks, 'RING_FINGER_TIP', 'PINKY_TIP'),

            # Four joints.
            self._get_distance_by_names(landmarks, 'WRIST', 'INDEX_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'WRIST', 'MIDDLE_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'WRIST', 'RING_FINGER_TIP'),
            self._get_distance_by_names(landmarks, 'WRIST', 'PINKY_TIP'),

            # Five joints.
            self._get_distance_by_names(landmarks, 'THUMB_TIP', 'MIDDLE_FINGER_MCP'),

        ])

        return embedding

    def _get_distance_by_names(self, landmarks, name_from, name_to):
        lmk_from = landmarks[self._landmark_names.index(name_from)]
        lmk_to = landmarks[self._landmark_names.index(name_to)]
        return self._get_distance(lmk_from, lmk_to)

    def _get_distance(self, lmk_from, lmk_to):
        return np.linalg.norm(lmk_to - lmk_from)

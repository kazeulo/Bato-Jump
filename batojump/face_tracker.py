"""Webcam capture and face detection."""
import cv2


class FaceTracker:
    def __init__(self, camera_index=0):
        self._cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._cap = cv2.VideoCapture(camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open webcam {camera_index}")
        self.width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        """Return a mirrored frame, or None if the camera failed."""
        ok, frame = self._cap.read()
        return cv2.flip(frame, 1) if ok else None

    def face_center_x(self, frame):
        """Horizontal center of the largest detected face, or None."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            return None
        x, _, w, _ = max(faces, key=lambda f: f[2] * f[3])
        return int(x + w // 2)

    def release(self):
        self._cap.release()

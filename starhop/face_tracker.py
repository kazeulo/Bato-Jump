"""Webcam capture and face detection (OpenCV YuNet)."""
import cv2

from . import config


class FaceDetector:
    """YuNet face detector that sticks to one person once it has locked on.

    YuNet is a small CNN detector: it copes with tilted heads, glasses, masks
    and uneven light far better than Haar cascades, and it is fast on CPU.
    """

    def __init__(self, model_path=config.FACE_MODEL, score_threshold=0.6,
                 lock_grace_frames=15):
        if not model_path.exists():
            raise FileNotFoundError(f"Face model not found: {model_path}")
        self._detector = cv2.FaceDetectorYN.create(
            str(model_path), "", (0, 0), score_threshold, 0.3, 5000)
        self._input_size = None
        self._lock_grace = lock_grace_frames
        self._locked_x = None  # center of the face we are following
        self._missed = 0

    def center_x(self, frame):
        """Horizontal center of the tracked face, or None if it is not visible."""
        size = (frame.shape[1], frame.shape[0])
        if size != self._input_size:
            self._detector.setInputSize(size)
            self._input_size = size

        _, faces = self._detector.detect(frame)
        face = self._pick(faces)
        if face is None:
            self._missed += 1
            if self._missed > self._lock_grace:
                self._locked_x = None  # lost them: next largest face takes over
            return None

        self._missed = 0
        self._locked_x = float(face[0] + face[2] / 2)
        return int(self._locked_x)

    def _pick(self, faces):
        """Largest face to start with, then whichever is nearest the last one."""
        if faces is None or len(faces) == 0:
            return None
        if self._locked_x is None:
            return max(faces, key=lambda f: f[2] * f[3])
        return min(faces, key=lambda f: abs(f[0] + f[2] / 2 - self._locked_x))


class FaceTracker:
    """Webcam + face detector."""

    def __init__(self, camera_index=0, detector=None):
        self._cap = cv2.VideoCapture(camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open webcam {camera_index}")
        self._detector = detector or FaceDetector()
        self.width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        """Return a mirrored frame, or None if the camera failed."""
        ok, frame = self._cap.read()
        return cv2.flip(frame, 1) if ok else None

    def face_center_x(self, frame):
        """Horizontal center of the tracked face, or None."""
        return self._detector.center_x(frame)

    def release(self):
        self._cap.release()

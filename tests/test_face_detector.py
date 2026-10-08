import cv2
import numpy as np
import pytest

from starhop import config
from starhop.face_tracker import FaceDetector

PHOTO = config.IMG / "title.png"  # contains a real face photo


@pytest.fixture
def frame():
    image = cv2.imread(str(PHOTO))
    assert image is not None
    return image


def test_detects_face_in_photo(frame):
    x = FaceDetector().center_x(frame)
    assert x is not None and 0 < x < frame.shape[1]


def test_no_face_returns_none(frame):
    blank = frame * 0
    assert FaceDetector().center_x(blank) is None


def _canvas(frame, small_x, big_x=None):
    """White canvas with a small face photo, and optionally a larger one."""
    canvas = np.full((400, 700, 3), 255, np.uint8)
    small = cv2.resize(frame, None, fx=1.0, fy=1.0)
    canvas[0:small.shape[0], small_x:small_x + small.shape[1]] = small
    if big_x is not None:
        big = cv2.resize(frame, None, fx=1.6, fy=1.6)
        canvas[0:big.shape[0], big_x:big_x + big.shape[1]] = big
    return canvas


def test_locks_onto_first_face_and_ignores_bigger_newcomer(frame):
    detector = FaceDetector()
    first = detector.center_x(_canvas(frame, small_x=20))
    assert first is not None

    both = _canvas(frame, small_x=20, big_x=290)
    detector_check = FaceDetector()
    detector_check.center_x(both)  # initialise input size
    _, faces = detector_check._detector.detect(both)
    assert len(faces) == 2  # sanity: the bigger newcomer really is visible

    assert abs(detector.center_x(both) - first) < 30  # still following the first
    assert FaceDetector().center_x(both) > 290  # an unlocked detector picks the larger one

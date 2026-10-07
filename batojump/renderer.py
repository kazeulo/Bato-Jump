"""Drawing the world onto a webcam frame."""
import cv2
import numpy as np

from . import config
from .config import PLATFORM, PLAYER


def _load_sprite(name, size):
    sprite = cv2.imread(str(config.IMG / name), cv2.IMREAD_UNCHANGED)
    if sprite is None:
        raise FileNotFoundError(config.IMG / name)
    sprite = cv2.resize(sprite, size)
    if sprite.shape[2] == 3:  # no alpha channel: make fully opaque
        alpha = np.full(sprite.shape[:2] + (1,), 255, dtype=sprite.dtype)
        sprite = np.concatenate([sprite, alpha], axis=2)
    return sprite


def overlay_sprite(frame, sprite, x, y):
    """Alpha-blend `sprite` onto `frame` at (x, y), clipping at the edges."""
    fh, fw = frame.shape[:2]
    sh, sw = sprite.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + sw, fw), min(y + sh, fh)
    if x0 >= x1 or y0 >= y1:
        return
    part = sprite[y0 - y:y1 - y, x0 - x:x1 - x]
    alpha = part[:, :, 3:4] / 255.0
    roi = frame[y0:y1, x0:x1]
    roi[:] = (roi * (1 - alpha) + part[:, :, :3] * alpha).astype(frame.dtype)


class Renderer:
    def __init__(self):
        self._player = _load_sprite("character_bato.png", (PLAYER.width, PLAYER.height))
        self._platform = _load_sprite("platform.png", (PLATFORM.width, PLATFORM.height))

    def draw(self, frame, world):
        overlay_sprite(frame, self._player, int(world.x), int(world.y))
        for px, py in world.platforms:
            overlay_sprite(frame, self._platform, int(px), int(py))
        cv2.putText(frame, f"Score: {world.score}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    def draw_game_over(self, frame, score):
        h = frame.shape[0]
        self._centered(frame, "GAME OVER", h // 2, 2, 3)
        self._centered(frame, f"Final Score: {score}", h // 2 + 40, 1, 2)

    @staticmethod
    def _centered(frame, text, y, scale, thickness):
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, _), _ = cv2.getTextSize(text, font, scale, thickness)
        cv2.putText(frame, text, ((frame.shape[1] - tw) // 2, y),
                    font, scale, (0, 0, 255), thickness)

"""Static game configuration and asset paths."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
IMG = ASSETS / "img"
SOUNDS = ASSETS / "sounds"

WINDOW_TITLE = "Bato Jump"
MENU_SIZE = (400, 300)
CAMERA_INDEX = 0
QUIT_KEY = ord("q")


@dataclass(frozen=True)
class Physics:
    gravity: int = 1
    jump_strength: int = -20
    scroll_line: int = 200  # player is pushed down to this y once above it


@dataclass(frozen=True)
class PlayerSpec:
    width: int = 50
    height: int = 50


@dataclass(frozen=True)
class PlatformSpec:
    width: int = 80
    height: int = 20
    min_gap_y: int = 80
    max_gap_y: int = 100
    min_x: int = 50


PHYSICS = Physics()
PLAYER = PlayerSpec()
PLATFORM = PlatformSpec()
MUSIC_VOLUME = 0.1
GAME_OVER_DELAY_MS = 2000
STEER_SMOOTHING = 0.5  # 0..1, fraction of the distance to the face covered per frame
GAP_GROWTH_PER_SCORE = 1 / 400  # platforms spread out as the score climbs
MAX_EXTRA_GAP = 50
HIGHSCORE_FILE = ROOT / "highscore.txt"

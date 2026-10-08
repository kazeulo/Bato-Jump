"""Persisted best score."""
from . import config


def load():
    try:
        return int(config.HIGHSCORE_FILE.read_text().strip())
    except (OSError, ValueError):
        return 0


def save(score):
    try:
        config.HIGHSCORE_FILE.write_text(str(score))
    except OSError:
        pass  # a read-only install shouldn't crash the game

import pygame

from starhop import config
from starhop.audio import Audio
from starhop.face_tracker import FaceTracker
from starhop.game import Game
from starhop.menu import show_menu


def main():
    pygame.init()
    tracker = FaceTracker(config.CAMERA_INDEX)
    try:
        game = Game(tracker, Audio())
        character = config.DEFAULT_CHARACTER
        while (character := show_menu(character)) is not None:
            game.run(character)
    finally:
        tracker.release()
        pygame.quit()


if __name__ == "__main__":
    main()

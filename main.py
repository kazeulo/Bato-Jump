import pygame

from batojump import config
from batojump.audio import Audio
from batojump.face_tracker import FaceTracker
from batojump.game import Game
from batojump.menu import show_menu


def main():
    pygame.init()
    tracker = FaceTracker(config.CAMERA_INDEX)
    try:
        game = Game(tracker, Audio())
        while show_menu():
            game.run()
    finally:
        tracker.release()
        pygame.quit()


if __name__ == "__main__":
    main()

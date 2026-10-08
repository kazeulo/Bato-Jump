"""Sound effects and background music."""
import pygame

from . import config


class Audio:
    def __init__(self):
        pygame.mixer.init()
        self.jump = pygame.mixer.Sound(str(config.SOUNDS / "jump.wav"))
        self.game_over = pygame.mixer.Sound(str(config.SOUNDS / "game_over.mp3"))
        self.start = pygame.mixer.Sound(str(config.SOUNDS / "start.wav"))
        pygame.mixer.music.load(str(config.SOUNDS / "background.mp3"))
        pygame.mixer.music.set_volume(config.MUSIC_VOLUME)

    def play_music(self):
        pygame.mixer.music.play(-1)

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.stop()

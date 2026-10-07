"""Pygame start menu."""
import pygame

from . import config


def _load(name, size):
    image = pygame.image.load(str(config.IMG / name))
    return pygame.transform.scale(image, size)


def show_menu():
    """Block until the user picks an option. Returns True to play, False to exit.

    The menu window is closed before returning so it doesn't linger behind the game.
    """
    pygame.display.init()
    try:
        return _run_menu()
    finally:
        pygame.display.quit()


def _run_menu():
    screen = pygame.display.set_mode(config.MENU_SIZE)
    pygame.display.set_caption(config.WINDOW_TITLE)

    title = _load("title.png", (180, 100))
    play = _load("play.png", (110, 35))
    cancel = _load("cancel.png", (110, 35))

    cx = screen.get_width() // 2
    title_rect = title.get_rect(midtop=(cx, 30))
    play_rect = play.get_rect(midtop=(cx, 160))
    cancel_rect = cancel.get_rect(midtop=(cx, 220))

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    return True
                if cancel_rect.collidepoint(event.pos):
                    return False

        screen.fill((255, 255, 255))
        screen.blit(title, title_rect)
        screen.blit(play, play_rect)
        screen.blit(cancel, cancel_rect)
        pygame.display.flip()
        clock.tick(60)

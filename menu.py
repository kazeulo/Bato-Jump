# menu.py
import pygame

# Initialize pygame
pygame.init()

def show_menu():
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Game Menu")

    # Load sprites
    title_sprite = pygame.image.load('img/title.png')
    play_button_sprite = pygame.image.load('img/play.png')
    exit_button_sprite = pygame.image.load('img/cancel.png')

    title_sprite = pygame.transform.scale(title_sprite, (180, 100))
    play_button_sprite = pygame.transform.scale(play_button_sprite, (110, 35))
    exit_button_sprite = pygame.transform.scale(exit_button_sprite, (110, 35))

    # Calculate center position for buttons and title
    title_x = (screen.get_width() - title_sprite.get_width()) // 2
    play_button_x = (screen.get_width() - 100) // 2
    exit_button_x = (screen.get_width() - 100) // 2
    title_y = 30 
    play_button_y = 160
    exit_button_y = 220

    title_rect = pygame.Rect(title_x, title_y, title_sprite.get_width(), title_sprite.get_height())
    play_button_rect = pygame.Rect(play_button_x, play_button_y, 100, 50)
    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, 100, 50)

    while True:
        screen.fill((255, 255, 255))

        # Add the elements
        screen.blit(title_sprite, title_rect.topleft)
        screen.blit(play_button_sprite, play_button_rect.topleft)
        screen.blit(exit_button_sprite, exit_button_rect.topleft)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Exit menu and stop
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    return True  # Start the game
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    return False  # Exit the game

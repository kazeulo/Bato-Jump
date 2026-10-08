"""Pygame start menu: animated title, pick a member, then play."""
import math

import pygame

from . import config, highscore

NEON = (190, 150, 255)
TEXT = (240, 232, 255)
MUTED = (160, 150, 200)
BUTTON = (60, 30, 120)
BUTTON_HOVER = (100, 58, 180)
PANEL = (12, 8, 40, 170)
SCROLL_SPEED = 18  # background pixels per second

NAMES = {"cyan": "CYAN", "holo": "HOLO", "lilac": "LILAC", "pink": "PINK"}


def _image(name, size):
    path = config.SPRITES / name
    return pygame.transform.smoothscale(pygame.image.load(str(path)).convert_alpha(), size)


def show_menu(selected=config.DEFAULT_CHARACTER):
    """Block until the user picks an option.

    Returns the chosen character name to start playing, or None to exit.
    The menu window is closed before returning so it does not linger behind the game.
    """
    pygame.display.init()
    try:
        return _Menu(selected).run()
    finally:
        pygame.display.quit()


class _Menu:
    def __init__(self, selected):
        self.selected = selected
        self.screen = pygame.display.set_mode(config.MENU_SIZE)
        pygame.display.set_caption(config.WINDOW_TITLE)
        width = self.screen.get_width()
        self.cx = width // 2
        self.best = highscore.load()
        self._load_assets()
        self._layout()

    def _load_assets(self):
        self.background = pygame.image.load(
            str(config.SPRITES / "background_tile_seamless.png")).convert()
        self.title_font = pygame.font.SysFont("arial", 50, bold=True)
        self.sub_font = pygame.font.SysFont("arial", 24, bold=True)
        self.button_font = pygame.font.SysFont("arial", 26, bold=True)
        self.label_font = pygame.font.SysFont("arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("arial", 15)

        self.title_line, self.subtitle = (
            self.title_font.render(config.TITLE_LINES[0], True, TEXT),
            self.sub_font.render(config.TITLE_LINES[1], True, NEON),
        )
        self.glow = self.title_font.render(config.TITLE_LINES[0], True, NEON)
        self.platform = _image("platform_normal.png", (66, 16))
        self.front = {n: _image(f"player_{n}_front.png", (50, 60)) for n in config.CHARACTERS}
        self.jump = {n: _image(f"player_{n}_jump_right.png", (50, 60)) for n in config.CHARACTERS}

    def _layout(self):
        card_w, card_h, gap = 76, 112, 12
        n = len(config.CHARACTERS)
        left = self.cx - (n * card_w + (n - 1) * gap) // 2
        self.cards = {
            name: pygame.Rect(left + i * (card_w + gap), 150, card_w, card_h)
            for i, name in enumerate(config.CHARACTERS)
        }
        self.play_rect = pygame.Rect(0, 0, 180, 46)
        self.play_rect.midtop = (self.cx - 100, 326)
        self.exit_rect = pygame.Rect(0, 0, 180, 46)
        self.exit_rect.midtop = (self.cx + 100, 326)
        self.help_rect = pygame.Rect(0, 0, 310, 44)
        self.help_rect.midtop = (self.cx, 386)

    # --- input -----------------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        while True:
            result = self._handle_events()
            if result is not _CONTINUE:
                return result
            self._draw(pygame.time.get_ticks() / 1000, pygame.mouse.get_pos())
            pygame.display.flip()
            clock.tick(60)

    def _handle_events(self):
        order = config.CHARACTERS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                index = order.index(self.selected)
                if event.key == pygame.K_LEFT:
                    self.selected = order[(index - 1) % len(order)]
                elif event.key == pygame.K_RIGHT:
                    self.selected = order[(index + 1) % len(order)]
                elif pygame.K_1 <= event.key < pygame.K_1 + len(order):
                    self.selected = order[event.key - pygame.K_1]
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.selected
                elif event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in self.cards.items():
                    if rect.collidepoint(event.pos):
                        self.selected = name
                if self.play_rect.collidepoint(event.pos):
                    return self.selected
                if self.exit_rect.collidepoint(event.pos):
                    return None
        return _CONTINUE

    # --- drawing ---------------------------------------------------------------
    def _draw(self, t, mouse):
        self._draw_background(t)
        self._draw_title(t)
        for name, rect in self.cards.items():
            self._draw_card(name, rect, t, rect.collidepoint(mouse))

        heading = self.small_font.render("CHOOSE YOUR PLAYER", True, MUTED)
        self.screen.blit(heading, heading.get_rect(midtop=(self.cx, 126)))
        label = self.label_font.render(NAMES[self.selected], True, NEON)
        self.screen.blit(label, label.get_rect(midtop=(self.cx, 270)))
        hint = self.small_font.render("< >  choose     Enter  play     Esc  exit", True, MUTED)
        self.screen.blit(hint, hint.get_rect(midtop=(self.cx, 292)))

        self._draw_button(self.play_rect, "PLAY", mouse)
        self._draw_button(self.exit_rect, "EXIT", mouse)
        self._draw_help()

    def _draw_background(self, t):
        tile_w, tile_h = self.background.get_size()
        y = -int(t * SCROLL_SPEED) % tile_h  # scroll downward, wrapping the tile
        for x in range(0, config.MENU_SIZE[0], tile_w):
            self.screen.blit(self.background, (x, y))
            self.screen.blit(self.background, (x, y - tile_h))

    def _draw_title(self, t):
        pulse = 0.5 + 0.5 * math.sin(t * 2)
        glow = self.glow.copy()
        glow.set_alpha(int(90 + 120 * pulse))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            self.screen.blit(glow, glow.get_rect(midtop=(self.cx + dx, 10 + dy)))
        self.screen.blit(self.title_line, self.title_line.get_rect(midtop=(self.cx, 10)))
        self.screen.blit(self.subtitle, self.subtitle.get_rect(midtop=(self.cx, 66)))
        if self.best:
            best = self.small_font.render(f"BEST  {self.best}", True, MUTED)
            self.screen.blit(best, best.get_rect(midtop=(self.cx, 97)))

    def _draw_card(self, name, rect, t, hovered):
        chosen = name == self.selected
        lift = -4 if hovered and not chosen else 0
        rect = rect.move(0, lift)

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((255, 255, 255, 55) if chosen else (10, 6, 30, 140))
        self.screen.blit(panel, rect)
        pygame.draw.rect(self.screen, NEON if chosen else MUTED, rect,
                         width=3 if chosen else 1, border_radius=10)

        platform_pos = self.platform.get_rect(midbottom=(rect.centerx, rect.bottom - 10))
        self.screen.blit(self.platform, platform_pos)
        if chosen:  # the selected member bounces on their platform
            bob = abs(math.sin(t * 4)) * 14
            sprite = self.jump[name]
            self.screen.blit(sprite, sprite.get_rect(midbottom=(rect.centerx,
                                                                platform_pos.top + 4 - bob)))
        else:
            sprite = self.front[name]
            self.screen.blit(sprite, sprite.get_rect(midbottom=(rect.centerx,
                                                                platform_pos.top + 4)))

    def _draw_button(self, rect, label, mouse):
        hovered = rect.collidepoint(mouse)
        grown = rect.inflate(8, 4) if hovered else rect
        pygame.draw.rect(self.screen, BUTTON_HOVER if hovered else BUTTON, grown,
                         border_radius=20)
        pygame.draw.rect(self.screen, NEON, grown, width=2, border_radius=20)
        text = self.button_font.render(label, True, TEXT)
        self.screen.blit(text, text.get_rect(center=grown.center))

    def _draw_help(self):
        panel = pygame.Surface(self.help_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, PANEL, panel.get_rect(), border_radius=10)
        self.screen.blit(panel, self.help_rect)
        lines = ("Move your head left / right to steer",
                 "In game:  P pause   Q menu   R retry")
        for i, text in enumerate(lines):
            surf = self.small_font.render(text, True, TEXT if i == 0 else MUTED)
            self.screen.blit(surf, surf.get_rect(midtop=(self.cx, self.help_rect.top + 4 + i * 17)))


_CONTINUE = object()

"""Pure game state and rules (no I/O), so it can be tested headlessly."""
import random
from dataclasses import dataclass, field

from .config import (GAP_GROWTH_PER_SCORE, MAX_EXTRA_GAP, PHYSICS, PLATFORM,
                     PLAYER, STEER_SMOOTHING)


@dataclass
class World:
    width: int
    height: int
    x: float = 0
    y: float = 0
    velocity: float = 0
    score: int = 0
    facing: int = 0  # -1 left, 1 right, 0 not moved yet (front pose)
    platforms: list = field(default_factory=list)

    def __post_init__(self):
        self.reset()

    def reset(self):
        first = (self.width // 2 - PLATFORM.width // 2, self.height - PLATFORM.height)
        self.platforms = [first]
        self.x = self.width // 2 - PLAYER.width // 2
        self.y = first[1] - PLAYER.height
        self.velocity = PHYSICS.jump_strength
        self.score = 0
        self.facing = 0
        self._fill_above()

    def move_to(self, center_x):
        """Place the player horizontally, clamped to the screen."""
        self._set_x(center_x - PLAYER.width // 2)

    def steer_toward(self, center_x):
        """Ease the player toward a target x so detector jitter doesn't shake it."""
        target = center_x - PLAYER.width // 2
        self._set_x(self.x + (target - self.x) * STEER_SMOOTHING)

    def _set_x(self, x):
        x = self._clamp_x(x)
        if x - self.x > 0.5:
            self.facing = 1
        elif self.x - x > 0.5:
            self.facing = -1
        self.x = x

    def _clamp_x(self, x):
        return max(0, min(x, self.width - PLAYER.width))

    @property
    def extra_gap(self):
        return min(MAX_EXTRA_GAP, int(self.score * GAP_GROWTH_PER_SCORE))

    def step(self):
        """Advance one tick. Returns True if the player bounced this tick."""
        self.velocity += PHYSICS.gravity
        self.y += self.velocity
        bounced = self._bounce()
        self._scroll()
        return bounced

    @property
    def game_over(self):
        return self.y > self.height

    def _bounce(self):
        if self.velocity <= 0:
            return False
        feet = self.y + PLAYER.height
        prev_feet = feet - self.velocity
        for px, py in self.platforms:
            overlaps_x = px < self.x + PLAYER.width and px + PLATFORM.width > self.x
            if overlaps_x and prev_feet <= py <= feet:
                self.velocity = PHYSICS.jump_strength
                self.y = py - PLAYER.height
                return True
        return False

    def _scroll(self):
        if self.y < PHYSICS.scroll_line:
            diff = PHYSICS.scroll_line - self.y
            self.y += diff
            self.platforms = [(px, py + diff) for px, py in self.platforms]
            self.score += int(diff)
        self.platforms = [p for p in self.platforms if p[1] <= self.height]
        self._fill_above()

    def _fill_above(self):
        top = min((py for _, py in self.platforms), default=self.height)
        while top > 0:
            top -= random.randint(PLATFORM.min_gap_y, PLATFORM.max_gap_y) + self.extra_gap
            x = random.randint(PLATFORM.min_x, self.width - PLATFORM.width)
            self.platforms.append((x, top))

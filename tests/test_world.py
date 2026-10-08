import numpy as np

from batojump.config import PLAYER
from batojump.renderer import overlay_sprite
from batojump.world import World


def test_player_bounces_on_start_platform_and_scores():
    w = World(640, 480)
    w.velocity = 0
    w.y = w.platforms[0][1] - PLAYER.height - 5  # just above the start platform
    assert any(w.step() for _ in range(5))  # lands and bounces
    assert w.velocity < 0


def test_falling_off_screen_is_game_over():
    w = World(640, 480)
    w.platforms = []
    w.velocity = 0
    w.y = 400
    for _ in range(100):
        w.step()
        if w.game_over:
            break
    assert w.game_over


def test_move_to_clamps_to_screen():
    w = World(640, 480)
    w.move_to(-100)
    assert w.x == 0
    w.move_to(10_000)
    assert w.x == 640 - PLAYER.width


def test_platforms_always_cover_screen_top():
    w = World(640, 480)
    for _ in range(500):
        w.step()
        if w.game_over:
            break
        assert min(py for _, py in w.platforms) <= 0


def test_overlay_clips_at_edges():
    frame = np.zeros((10, 10, 3), np.uint8)
    sprite = np.full((5, 5, 4), 255, np.uint8)
    overlay_sprite(frame, sprite, -2, 8)
    overlay_sprite(frame, sprite, 20, 20)  # fully off-screen: no-op
    assert frame.sum() == 3 * 255 * 3 * 2


def test_steering_eases_toward_target_without_overshoot():
    w = World(640, 480)
    w.move_to(100)
    start = w.x
    w.steer_toward(500)
    assert start < w.x < 500 - PLAYER.width // 2


def test_platform_gaps_grow_with_score_but_are_capped():
    w = World(640, 480)
    assert w.extra_gap == 0
    w.score = 10**9
    assert 0 < w.extra_gap <= 50


def test_highscore_roundtrip(tmp_path, monkeypatch):
    from batojump import config, highscore
    monkeypatch.setattr(config, "HIGHSCORE_FILE", tmp_path / "hs.txt")
    assert highscore.load() == 0
    highscore.save(42)
    assert highscore.load() == 42

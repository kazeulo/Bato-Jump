"""One play session: webcam in, rendered frames out."""
import cv2

from . import config
from .audio import Audio
from .face_tracker import FaceTracker
from .renderer import Renderer
from .world import World


class Game:
    def __init__(self, tracker: FaceTracker, audio: Audio):
        self.tracker = tracker
        self.audio = audio
        self.renderer = Renderer()
        self.world = World(tracker.width, tracker.height)

    def run(self):
        """Play until game over or quit key. Returns True if the player died."""
        self.world.reset()
        self.audio.start.play()
        self.audio.play_music()
        try:
            while True:
                frame = self.tracker.read()
                if frame is None:
                    return False

                center_x = self.tracker.face_center_x(frame)
                if center_x is not None:
                    self.world.move_to(center_x)

                if self.world.step():
                    self.audio.jump.play()

                if self.world.game_over:
                    self._show_game_over(frame)
                    return True

                self.renderer.draw(frame, self.world)
                cv2.imshow(config.WINDOW_TITLE, frame)
                if cv2.waitKey(1) & 0xFF == config.QUIT_KEY:
                    return False
        finally:
            self.audio.stop_music()
            cv2.destroyAllWindows()

    def _show_game_over(self, frame):
        self.audio.stop_music()
        self.audio.game_over.play()
        self.renderer.draw_game_over(frame, self.world.score)
        cv2.imshow(config.WINDOW_TITLE, frame)
        cv2.waitKey(config.GAME_OVER_DELAY_MS)

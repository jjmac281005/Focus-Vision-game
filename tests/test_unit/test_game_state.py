import unittest
from services.game_state import pencil_state, brodie_state


class TestGameState(unittest.TestCase):

    def test_pencil_pause(self):
        pencil_state["paused"] = True
        self.assertTrue(pencil_state["paused"])

    def test_pencil_reset(self):
        pencil_state["reset"] = True
        self.assertTrue(pencil_state["reset"])

    def test_brodie_pause(self):
        brodie_state["paused"] = True
        self.assertTrue(brodie_state["paused"])

    def test_brodie_reset(self):
        brodie_state["reset"] = True
        self.assertTrue(brodie_state["reset"])
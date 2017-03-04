import unittest
from pyrogi.backend import Screen, Backend
from pyrogi.util.vector import Vec2

class TestScreen(Screen):
    pass

class TestBackend(unittest.TestCase):
    def test_screens(self):
        backend = Backend(Vec2(0, 0), Vec2(0, 0), '', TestScreen())
        self.assertEqual(len(backend.screens), 1)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 2)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 3)

        backend.go_back_n_screens(1)
        self.assertEqual(len(backend.screens), 2)

        backend.set_screen(TestScreen())
        self.assertEqual(len(backend.screens), 3)

        backend.go_back_n_screens(2)
        self.assertEqual(len(backend.screens), 1)

        backend.go_back_n_screens(1)
        self.assertEqual(len(backend.screens), 0)

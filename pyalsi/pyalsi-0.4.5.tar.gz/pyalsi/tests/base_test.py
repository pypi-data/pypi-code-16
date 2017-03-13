import unittest

from click.testing import CliRunner


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

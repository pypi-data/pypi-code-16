"""Tests for our `pwdc create` subcommand."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase


class TestCreate(TestCase):

    def test_returns_no_session(self):
        output = popen(['pwdc', 'env'], stdout=PIPE).communicate()[0]
        self.assertTrue('No PWD Session, check --session_file parameter' in output)

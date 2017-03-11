from mate import TestCase
from mate.matchers import Mismatch


class AlwaysMatcher(object):
    """
    I always match. I'm just agreeable that way.

    """

    def match(self, result):
        return None


class NeverMatcher(object):
    """
    I never match. I'm not like that other guy, he's crazy.

    """

    def match(self, result):
        return Mismatch("Can't you read? I never match!")


class TestAssertThat(TestCase):
    def test_successful_matches_are_successful_tests(self):
        self.assertThat(1, AlwaysMatcher())

    def test_unsuccessful_matches_are_unsuccessful_tests(self):
        with self.assertRaises(self.failureException) as e:
            self.assertThat(1, NeverMatcher())
        self.assertEqual(str(e.exception), "Can't you read? I never match!")

from unittest import TestCase as PyUnitTestCase


class MatcherSupportMixin(object):
    def assertThat(self, result, matcher):
        """
        Assert that the result matches via the given matcher.

        Arguments:

            result (object):

                the result to try and match

            matcher (Matcher):

                the Matcher to use

        """

        mismatch = matcher.match(result)
        if mismatch is not None:
            self.fail(mismatch.describe())


class TestCase(MatcherSupportMixin, PyUnitTestCase):
    pass

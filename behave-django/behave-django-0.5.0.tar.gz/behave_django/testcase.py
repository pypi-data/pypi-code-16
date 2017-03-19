from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.testcases import TestCase


class BehaviorDrivenTestCase(StaticLiveServerTestCase):
    """
    Test case attached to the context during behave execution

    This test case prevents the regular tests from running.
    """

    def runTest(self):
        pass


class ExistingDatabaseTestCase(BehaviorDrivenTestCase):
    """
    Test case used for the --use-existing-database setup

    This test case prevents fixtures from being loaded to the database in use.
    """

    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass


class DjangoSimpleTestCase(TestCase):
    """
    Test case attached to the context during behave execution

    This test case uses `transaction.atomic()` to achieve test isolation
    instead of flushing the entire database. As a result, tests run much
    quicker and have no issues with altered DB state after all tests ran
    when `--keepdb` is used.

    As a side effect, this test case does not support web browser automation.
    Use Django's testing client instead to test requests and responses.

    Also, it prevents the regular tests from running.
    """

    def runTest(self):
        pass

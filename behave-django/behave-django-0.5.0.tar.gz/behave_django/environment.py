from behave.runner import ModelRunner, Context
from django.core.management import call_command
from django.shortcuts import resolve_url


class PatchedContext(Context):

    @property
    def base_url(self):
        assert hasattr(self.test, 'live_server_url'), (
            'Web browser automation is not available.'
            ' This scenario step can not be run'
            ' with the --simple or -S flag.')
        return self.test.live_server_url

    def get_url(self, to=None, *args, **kwargs):
        return self.base_url + (
            resolve_url(to, *args, **kwargs) if to else '')


class BehaveHooksMixin(object):
    """
    Provides methods that run during test execution

    These methods are attached to behave via monkey patching.
    """
    testcase_class = None

    def before_scenario(self, context):
        """
        Method that runs before behave's before_scenario function

        Sets up the test case, base_url, and the get_url() utility function.
        """
        context.__class__ = PatchedContext
        # Simply setting __class__ directly doesn't work
        # because behave.runner.Context.__setattr__ is implemented wrongly.
        object.__setattr__(context, '__class__', PatchedContext)

        context.test = self.testcase_class()
        context.test.setUpClass()
        context.test()

    def load_fixtures(self, context):
        """
        Method that runs immediately after behave's before_scenario function

        If fixtures are found in context, loads the fixtures using the loaddata
        management command.
        """
        if getattr(context, 'fixtures', None):
            call_command('loaddata', *context.fixtures, verbosity=0)

    def after_scenario(self, context):
        """
        Method that runs immediately after behave's after_scenario function
        """
        context.test.tearDownClass()
        del context.test


def monkey_patch_behave(django_test_runner):
    """
    Integrate behave_django in behave via before/after scenario hooks
    """
    behave_run_hook = ModelRunner.run_hook

    def run_hook(self, name, context, *args):
        if name == 'before_scenario':
            django_test_runner.before_scenario(context)
        behave_run_hook(self, name, context, *args)
        if name == 'before_scenario':
            django_test_runner.load_fixtures(context)
        if name == 'after_scenario':
            django_test_runner.after_scenario(context)

    ModelRunner.run_hook = run_hook

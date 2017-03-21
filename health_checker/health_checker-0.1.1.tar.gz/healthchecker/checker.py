import inspect


CHECK_TOKEN = '__is_check'


def check(func):
    setattr(func, CHECK_TOKEN, True)
    return func


class CheckCase(object):
    """
    Runs checks to verity if things are working or not.

    All methods which are decorated with "@check" is run. If it returns
    False or raises an Exception, its check is considered a failure,
    and will be reported as False (not working).

    You must call "self.check()" manually in your class to start the magic.
    """
    check_report = {}

    def check(self):
        """
        Run all checks, stores the results on 'check_report' and
        returns true if checks succeeded, otherwise returns false

        :rtype: bool
        :return: Whether the check has succeeded or not
        """
        check_methods = self._get_check_methods()

        self.check_report = {check_name: self.__run_check(check_method)
                             for check_name, check_method in check_methods}

        return self.has_succeeded()

    def __run_check(self, method):
        try:
            return method()
        except:
            return False

    def has_succeeded(self):
        """
        Verifies if report has only successes.
        If there is nothing in report, returns True

        :rtype: bool
        """
        return True if not self.check_report \
            else all(self.check_report.values())

    def _get_check_methods(self):
        all_methods = inspect.getmembers(self, predicate=inspect.ismethod)

        for method_name, method in all_methods:
            if self._is_check_method(method):
                yield method_name, method

    def _is_check_method(self, method):
        return getattr(method, CHECK_TOKEN, False)
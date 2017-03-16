from faker import Factory
from lazyutils import delegate_to

from funspec.exceptions import BuildError
from funspec.mod import FunspecMod, TestMod
from funspec.result import Result, ErrorResult

fake = Factory.create()


class Grader:
    """
    Represents a Funspec testing module.

    Usage:

        >>> grader = Grader(mod_source)
        >>> results = grader.run_tests(input_source, lang='python')
        >>> results.is_correct()
        True
    """

    source = delegate_to('funspec')
    num_cases = delegate_to('funspec')

    def __init__(self, source, num_cases=100):
        self.funspec = FunspecMod(source, num_cases)

        # Create a code object associated with the module source code
        try:
            self.funspec.build()
            self.error = None
            self.error_message = ''
            self._valid = True
        except BuildError as ex:
            self.error_message = ex.message
            self.error = ex
            self._valid = False

    def is_valid(self):
        """
        Returns True if input funspec mod source code is valid.

        Only valid modules can test code.
        """

        return self._valid

    def supports_language(self, lang):
        """
        Returns True, if the given programming language is supported by the
        given funspec module.
        """

        # For now, we only support python
        return self._valid and lang == 'python'

    def run_tests(self, source, lang, force_result=False, stop_at_error=False):
        """
        Test the given source code

        Args:
            source (str):
                Input source code string.
            lang (str):
                Input programming language.
            force_result (bool):
                Return an ErrorResult object even if module is invalid.

        Returns:
            A :cls:`funspec.TestResult` object.
        """

        if not self.is_valid():
            if force_result:
                return ErrorResult('module-error', self.error_message)
            raise ValueError('cannot test code based on an invalid funspec '
                             'module')

        if not self.supports_language(lang):
            msg = 'this modules does not support %s' % lang
            if force_result:
                return ErrorResult('module-error', 'LanguageError: ' + msg)
            raise ValueError(msg)

        test_mod = TestMod(source, self.funspec, lang=lang)
        try:
            test_mod.build()
        except BuildError as ex:
            return ErrorResult('build-error', ex.message)

        return Result(test_mod.run_tests(stop_at_error))


def format_error(ex):
    """
    Format syntax error into a error_message string.
    """

    return str(ex)

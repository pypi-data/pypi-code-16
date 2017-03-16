import collections

from funspec.answer_key import AnswerKey
from funspec.exceptions import BuildError
from funspec.testcase import AnswerKeyTestCase, ExecutionErrorTestCase, \
    MissingFunctionTestCase
from funspec.utils import capture_output


class BaseMod(collections.Mapping):
    """
    Base class for FunspecMod and TestMod.

    Expose functions and symbols defined in module as a dictionary.
    It is initialized with a string of source code and it requires a .build()
    step which populates the internal dictionary with symbol definitions.
    """

    def __init__(self, source):
        self.source = source
        self.built = False
        self._data = {}

    def __len__(self):
        self._assure_built()
        return len(self._data)

    def __iter__(self):
        self._assure_built()
        return iter(self._data)

    def __getitem__(self, key):
        self._assure_built()
        return self._data[key]

    def _assure_built(self):
        if not self.built:
            raise RuntimeError(
                'cannot execute this function before calling the .build() '
                'method.'
            )

    def build(self):
        """
        Populate the symbols in the namespace from the module's source code.

        Subclasses must implement this method and remember to set build=True
        in the end of a successful build. Unsuccessful builds should raise
        BuildError.
        """

        raise NotImplementedError(
            'Subclasses must implement the build method and remember to set'
            'build = True in the end of the build phase.'
        )


class FunspecMod(BaseMod):
    """
    Expose the Funspec module as a dictionary of function definitions.

    Usage:
        After creating a new new instance from a source code string or file,
        we must call the .build() method to retrieve symbols

        >>> ns = FunspecMod(source)
        >>> ns.build()           # raise BuildErrors in case of problems
        >>> ns['some_function']  # now we can access module as a dictionary
    """

    def __init__(self, source, num_examples=100):
        super().__init__(source)
        self.num_examples = num_examples
        self._answer_key_examples = None

    def build(self):
        try:
            code = compile(self.source, '<funspec>', 'exec')
            exec(code, builtins(), self._data)
        except Exception as ex:
            msg = 'error while building Funspec module'
            raise BuildError.from_exception(ex, msg=msg)
        self.built = True

    def answer_keys(self):
        """
        Return a dictionary with all answer keys in the namespace.
        """

        return {name: AnswerKey(function, name)
                for name, function in self.items()
                if getattr(function, '_is_answer_key', False)}

    def answer_key_examples(self, keep_errors=False):
        """
        Return a dictionary of (function, example_list) pairs.

        Args:
            keep_errors (bool):
                If True, create ErrorExample() objects when the answer_key
                functions fail. Otherwise, raise an AnswerKeyError exception.

        Return:
            Each example in the example_list is an :cls:`funspec.Example`
            instance.
        """

        if self._answer_key_examples is None:
            self._answer_key_examples = {
                key: answer_key.examples(self.num_examples, keep_errors)
                for key, answer_key in self.answer_keys().items()}
        return self._answer_key_examples


class TestMod(BaseMod):
    """
    Expose functions defined by user/student as a dictionary.
    """

    def __init__(self, source, funspecmod, lang):
        super().__init__(source)
        self.funspecmod = funspecmod
        self.lang = lang

    def build(self):
        try:
            code = compile(self.source, '<testmod>', 'exec')
            exec(code, {}, self._data)
        except Exception as ex:
            msg = 'error while building test module'
            raise BuildError.from_exception(ex, msg=msg)
        self.built = True

    def run_tests(self, stop_at_error=False):
        """
        Iterates over all test cases returning their corresponding results.
        """

        for item in self.run_answer_key_tests(stop_at_error):
            yield item
        for item in self.run_pytest_tests(stop_at_error):
            yield item

    def run_answer_key_tests(self, stop_at_error=False):
        """
        Run answer key test cases
        """

        examples = self.funspecmod.answer_key_examples()
        for func_name, examples in examples.items():
            # Check if function was defined in the test mod.
            try:
                func = self[func_name]
            except KeyError:
                missing = MissingFunctionTestCase(func_name)
                if not stop_at_error:
                    for _ in examples:
                        yield missing
                else:
                    yield missing
                    return

            # Creates the test case objects by running the test function and
            # comparing the results with the reference values
            for args, result, output in examples:
                try:
                    with capture_output() as out:
                        res = func(*args)
                except Exception as ex:
                    yield ExecutionErrorTestCase(func_name, args, ex,
                                                 expected_output=output,
                                                 expected_result=result)
                    if stop_at_error:
                        return
                else:
                    key = AnswerKeyTestCase(func_name, args, res, out,
                                            expected_output=output,
                                            expected_result=result)
                    yield key
                    if stop_at_error and not key.is_correct():
                        return

    def run_pytest_tests(self, stop_at_error=False):
        """
        Run all tests that uses pytest.
        """

        if False:
            yield
        return


def builtins():
    """
    Return a dictionary of builtins.
    """

    from funspec import builtins
    return vars(builtins)

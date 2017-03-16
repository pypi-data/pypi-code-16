from funspec.exceptions import ExecutionError


class TestCase:
    def is_correct(self):
        raise NotImplementedError('%s must implement the is_correct method')


class ErrorTestCase(TestCase):
    """
    Base Class for all test cases that resulted in errors.
    """

    def is_correct(self):
        return False

    def __init__(self, error_type, error_message):
        self.error_type = error_type
        self.error_message = error_message


class PytestTestCase(TestCase):
    pass


class AnswerKeyTestCase(TestCase):
    """
    An answer key test case represents the result of execution of a function
    with a set of input arguments.

    It is one of the simplest function-based testing strategies, and is
    implemented in a Funspec module by functions decorated with the
    @answer_key decorator.

    Attributes:
        name (str):
            Name of the tested function.
        args (tuple):
            A tuple of arguments passed to the function.
        result:
            The result of function execution.
        output (str):
            Any eventual print output collected during function execution.
        is_correct (True/False/None):
            Optional argument that can be given to tell if test case is correct
            or not.
    """

    def is_correct(self):
        return self.result == self.expected_result

    def __init__(self, name, args, result, output=None, expected_result=None,
                 expected_output=None):
        self.name = name
        self.args = tuple(args)
        self.result = result
        self.expected_result = expected_result

    def __repr__(self):
        name = self.__class__.__name__
        func = self.name
        inputs = self.args
        result = self.result
        return '%s(%r, %r, %r)' % (name, func, inputs, result)


class MissingFunctionTestCase(ErrorTestCase):
    """
    Represent the situation in which an answer key function was not defined in
    the test module.
    """

    def __init__(self, name):
        self.name = name
        super().__init__('mising-function',
                         '%s function was not defined.' % name)


class ExecutionErrorTestCase(ErrorTestCase, AnswerKeyTestCase):
    """
    Represent an invalid AnswerKey execution that resulted in an error.
    """
    def __init__(self, name, args, error, **kwargs):
        kwargs['output'] = ExecutionError.from_exception(error).message
        AnswerKeyTestCase.__init__(self, name, args, None, **kwargs)
        self.error = error
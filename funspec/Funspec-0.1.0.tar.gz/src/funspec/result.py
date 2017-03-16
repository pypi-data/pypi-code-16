import collections
from _pydecimal import Decimal


class Result(collections.Sequence):
    """
    Report the results of Funspec test cases.
    """

    def is_correct(self):
        return all(x.is_correct() for x in self.data)

    def __init__(self, data=()):
        self.data = list(data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def _header(self):
        return ' (%s cases)' % len(self)

    def grade(self, method='ratio'):
        """
        Grade report object by judging the ratio of correct/incorrect answers.

        Args:
            method (str):
                The adopted grading strategy. Can be any of:
                    'ratio':
                        Grade is proportional to the fraction of correct tests.
                    'binary':
                        Users must pass all tests to achieve full grade.
                        Otherwise the grade is zero.

        Returns:
            Returns a decimal grade in the 0-100 range.
        """

        total = len(self.data)
        correct = sum(1 for x in self.data if x.is_correct())

        if method == 'ratio':
            return Decimal(100) * correct / total
        elif method == 'binary':
            return Decimal(100) if total == correct else Decimal(0)
        else:
            raise ValueError('invalid grading method: %r' % method)

    def report(self):
        """
        A human-friendly report.
        """

        print((
            '{classname}{header}:\n'
            '  success: {ratio}%\n'
            '  is correct: {is_correct}\n'
        ).format(
            classname=self.__class__.__name__,
            header=self._header(),
            ratio=self.grade('ratio'),
            is_correct=self.is_correct(),
        ))


class ErrorResult(Result):
    """
    A report subclass for reporting critical errors.
    """

    def is_correct(self):
        return False

    def __init__(self, error_type, error_message):
        super().__init__()
        self.error_type = error_type
        self.error_message = error_message

    def _header(self):
        message = self.error_message
        message = '\n'.join('      ' + line for line in message.splitlines())
        return ('\n  error: {error_type}\n'
                '  error_message:\n{message}').format(
            error_type=self.error_type,
            message=message
        )

    def grade(self, method='ratio'):
        return Decimal(0)
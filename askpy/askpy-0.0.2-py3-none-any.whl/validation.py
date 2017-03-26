from .compat import basestring
from .exceptions import ValidationError


class Validator(object):
    """This has no actual state but houses like-minded functions"""

    @staticmethod
    def num(resp):
        """Ensure a response is number-esque"""
        try:
            resp = int(resp)
        except ValueError:
            raise ValidationError('Please enter a number')
        return True

    @staticmethod
    def required(resp):
        """Ensure a response exists"""
        if not resp:
            raise ValidationError('Please enter a response')
        return True

    @staticmethod
    def positive_num(resp):
        """Ensure a response is number-esque and greater than 0"""
        Validator.num(resp)
        if int(resp) <= 0:
            raise ValidationError('Please enter a number greater than 0')
        return True

    @staticmethod
    def num_gt(min_number):
        """Ensure a string is longer than a min_number"""
        Validator.num(min_number)
        def is_at_least(resp):
            Validator.num(resp)
            if int(resp) <= min_number:
                raise ValidationError('Please enter a number greater than %d' % min_number)
            return True
        return is_at_least

    @staticmethod
    def num_gte(min_number):
        """Ensure a string is longer than or equal to a min_number"""
        Validator.num(min_number)
        def is_at_least(resp):
            Validator.num(resp)
            if int(resp) < min_number:
                raise ValidationError('Please enter a number greater than or equal to %d' % min_number)
            return True
        return is_at_least

    @staticmethod
    def num_lt(max_number):
        """Ensure a string is shorter than a min_number"""
        Validator.num(max_number)
        def is_at_most(resp):
            Validator.num(resp)
            if int(resp) >= max_number:
                raise ValidationError('Please enter a number less than %d' % max_number)
            return True
        return is_at_most

    @staticmethod
    def num_lte(max_number):
        Validator.num(max_number)
        """Ensure a string is shorter than or equal to a min_number"""
        def is_at_most(resp):
            Validator.num(resp)
            if int(resp) > max_number:
                raise ValidationError('Please enter a number less than or equal to %d' % max_number)
            return True
        return is_at_most

    @staticmethod
    def num_between(min_num, max_num):
        """Ensure a number is between two numbers, boundaries included"""
        Validator.num(min_num)
        Validator.num(max_num)
        if int(min_num) > int(max_num):
            raise ValidationError('Your minimum number should not be larger than your max number')
        def is_between(resp):
            Validator.num_gte(min_num)(resp)
            Validator.num_lte(max_num)(resp)
            return True
        return is_between

    @staticmethod
    def len_gt(min_length):
        """Ensure a string is longer than a min_length"""
        def is_at_least(resp):
            if len(resp) <= min_length:
                raise ValidationError('Please enter response longer than %d characters' % min_length)
            return True
        return is_at_least

    @staticmethod
    def len_gte(min_length):
        """Ensure a string is longer than or equal to a min_length"""
        def is_at_least(resp):
            if len(resp) < min_length:
                raise ValidationError('Please enter response longer than or as long as %d characters' % min_length)
            return True
        return is_at_least

    @staticmethod
    def len_lt(max_length):
        """Ensure a string is shorter than a min_length"""
        def is_at_most(resp):
            if len(resp) >= max_length:
                raise ValidationError('Please enter response shorter than %d characters' % max_length)
            return True
        return is_at_most

    @staticmethod
    def len_lte(max_length):
        """Ensure a string is shorter than or equal to a min_length"""
        def is_at_most(resp):
            if len(resp) > max_length:
                raise ValidationError('Please enter response shorter than or as long as %d characters' % max_length)
            return True
        return is_at_most

    @staticmethod
    def one_of(options):
        """Ensure a response is one of the given options"""
        assert isinstance(options, list)
        def is_in(resp):
            if resp not in options:
                raise ValidationError('Please choose one of "%s"' % ' or '.join(options))
            return True
        return is_in

    @staticmethod
    def contains(options):
        """Ensure a response contains specified characters"""
        if not isinstance(options, basestring) and not isinstance(options, list):
            raise Exceptipn('Your contains object should be an iterable')
        def _contains(resp):
            for char in options:
                if char not in resp:
                    raise ValidationError('Please include the following characters: %s'% ', '.join(options))
            return True
        return _contains

    @staticmethod
    def matches(regex):
        """Ensure a response pattern matches a regex pattern"""
        import re
        def _matches(resp):
            pattern = re.compile(regex)
            if not pattern.match(resp):
                raise ValidationError('Please format your response to match %s' % regex)
            return True
        return _matches

import re
from datetime import datetime


class ParseError(Exception):
    def __init__(self, error_code, message):
        super().__init__(message)
        self.error_code = error_code

class ParseErrors(Exception):
    def __init__(self, errors):
        super().__init__()
        self.errors = errors

class RequestArguments(): # pylint: disable=too-few-public-methods
    def __init__(self, arguments):
        self.fields = [arg for arg in arguments if isinstance(arg, FieldsArgument)]
        assert len(self.fields) < 2, "Should not end up with multiple fields"
        self.fields = self.fields[0] if self.fields else None
        self.filters = [arg for arg in arguments if isinstance(arg, FilterArgument)]
        self.sorts = [arg for arg in arguments if isinstance(arg, SortArgument)]
        self.sorts = self.sorts[0] if self.sorts else None

class RequestArgument(): # pylint: disable=too-few-public-methods
    def __init__(self, queryarg, values):
        self.queryarg = queryarg
        self.values   = values

class FilterArgument(RequestArgument): # pylint: disable=too-few-public-methods
    EQ  = '='
    GT  = '>'
    GTE = '>='
    LT  = '<'
    LTE = '<='
    def __init__(self, queryarg, values):
        super().__init__(queryarg, values)
        if len(values) > 1:
            raise ParseError(
                error_code='filter-property-specified-more-than-once',
                message=("Your requested filter property, '{}', was specified more than once."
                    " We don't currently support that").format(queryarg))

        argname = queryarg[6:]
        if not argname:
            raise ParseError(
                error_code='empty-filter-name',
                message=("You requested a filter with no name."
                    " Filter requests should be of the form 'filter[property]'"))
        if argname[-1] == ']':
            self.operation = self.EQ
            self.handle_standard_queryarg(argname, values)
        elif argname[-2:] == ']<':
            self.operation = self.LTE
            self.handle_standard_queryarg(argname, values)
        elif argname[-2:] == ']>':
            self.operation = self.GTE
            self.handle_standard_queryarg(argname, values)
        elif not re.match(r'\[\w+\]', argname):
            raise ParseError(
                error_code='invalid-filter-request',
                message=("You requested a filter 'filter{}'. Filter requests should be of the form 'filter[property]'".format(argname)))
        else:
            self.handle_nonstandard_queryarg(argname, values)

        if not self.values:
            raise ParseError(
                error_code='empty-filter-value',
                message=("You requested a filter with no values. This won't match anything, ever"))

    def handle_nonstandard_queryarg(self, argname, values):
        if values and not '' in values:
            raise ParseError(
                error_code='invalid-filter-request',
                message=(("You requested a filter 'filter{}={}' with an equal in the value. "
                    "Filter requests should be of the form 'filter[property]=value'").format(argname, values[0])))

        match = re.match(r'\[(?P<name>\w+)\](?P<operation>\<|\>)(?P<values>[ ,\w,-]+)$', argname)
        if not match:
            raise ParseError(
                error_code='invalid-filter-request',
                message=("You requested a filter 'filter{}'. Filter requests should be of the form 'filter[property]'".format(argname)))
        if match.group('operation') == '<':
            self.operation = self.LT
        elif match.group('operation') == '>':
            self.operation = self.GT
        else:
            raise ParseError(error_code='programmer-error', message="Programming assertion failed. Tell Authentise support")

        self.name = match.group('name')
        self.values = match.group('values').split(',')

    def handle_standard_queryarg(self, argname, values):
        try:
            self.values = values[0].split(',')
        except IndexError:
            self.values = []

        if not argname[0] == '[':
            raise ParseError(
                error_code='invalid-filter-request',
                message=("You requested a filter 'filter{}'."
                    " Filter requests should be of the form 'filter[property]'").format(argname))

        self.name = argname[1:(-1 if self.operation == self.EQ else -2)]
        if not self.name:
            raise ParseError(
                error_code='empty-filter-name',
                message=("You requested a filter 'filter{}' with no name."
                    " Filter requests should be of the form 'filter[property]'").format(argname))

    def __str__(self):
        formatted_values = [value.isoformat() if isinstance(value, datetime) else str(value) for value in self.values]
        return "FilterArgument({}={})".format(self.name, ','.join(formatted_values))

    def __repr__(self):
        return str(self)

class SortArgument(RequestArgument): # pylint: disable=too-few-public-methods
    def __init__(self, queryarg, values):
        super().__init__(queryarg, values)

        if len(queryarg) > 4:
            raise ParseError(
                error_code='invalid-sort-request',
                message=("You requested a sort '{}'. "
                    "Sort requests should be of the form 'sort'".format(queryarg)))
        if len(values) > 1:
            suggestion = "sort={}".format(','.join(sorted(values)))
            raise ParseError(
                error_code='sort-property-specified-more-than-once',
                message=("You specified sort more than once. We don't support that. "
                         "Please combine multiple sort using a comma such as {}").format(suggestion))
        if len(values) < 1:
            raise ParseError(
                error_code='empty-sort-value',
                message=("You requested a sort with no values. You must provide at least one sort value."))

        _sort = values[0]
        _sort = _sort.split(',')
        self.values = [f.strip() for f in _sort]

        if len(set([value.lstrip('-') for value in self.values])) != len(self.values):
            raise ParseError(
                error_code='invalid-sort-request',
                message=("You requested a sort of the same field multiple times. You may only sort each field once."))


    def __str__(self):
        return "SortArgument({})".format(', '.join(self.values))

    def __repr__(self):
        return str(self)

class FieldsArgument(RequestArgument): # pylint: disable=too-few-public-methods
    def __init__(self, queryarg, values):
        super().__init__(queryarg, values)
        if len(values) > 1:
            suggestion = "fields=[{}]".format(','.join(sorted(values)))
            raise ParseError(
                    error_code='fields-property-specified-more-than-once',
                    message=("You specified fields more than once. We don't support that. "
                             "Please combine multiple fields using a comma such as {}").format(suggestion))

        _fields = values[0]
        if not (_fields[0] == '[' and _fields[-1] == ']'):
            raise ParseError(
                error_code='invalid-fields-query',
                message=("You specified a fields value of '{}'. Fields must be specified "
                        "as a comma-separated list of fields enclosed in '[' and ']'")
                        .format(_fields)
                )
        _fields = _fields[1:-1]
        _fields = _fields.split(',')
        self.values = [f.strip() for f in _fields]

ARGUMENT_PATTERNS = {
    re.compile(r'filter')   : FilterArgument,
    re.compile(r'fields')   : FieldsArgument,
    re.compile(r'sort')     : SortArgument,
}
def _get_matching_pattern(queryarg):
    for pattern, cls in ARGUMENT_PATTERNS.items():
        match = pattern.match(queryarg)
        if match:
            return cls
    raise ParseError('unrecognized-query-argument', 'The query argument {} is not recognized by this endpoint'.format(queryarg))

def parse_arguments(queryargs):
    arguments = []
    errors = []
    for queryarg in queryargs.keys():
        try:
            cls = _get_matching_pattern(queryarg)

            values = queryargs.getlist(queryarg)
            argument = cls(queryarg, values)
            arguments.append(argument)
        except ParseError as e:
            errors.append(e)
    if errors:
        raise ParseErrors(errors=errors)
    return RequestArguments(arguments)

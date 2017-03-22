# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
ESC [ 0 m       # reset all (colors and brightness)
ESC [ 1 m       # bright
ESC [ 2 m       # dim (looks same as normal brightness)
ESC [ 22 m      # normal brightness

# FOREGROUND:
ESC [ 30 m      # black
ESC [ 31 m      # red
ESC [ 32 m      # green
ESC [ 33 m      # yellow
ESC [ 34 m      # blue
ESC [ 35 m      # magenta
ESC [ 36 m      # cyan
ESC [ 37 m      # white
ESC [ 39 m      # reset

# BACKGROUND
ESC [ 40 m      # black
ESC [ 41 m      # red
ESC [ 42 m      # green
ESC [ 43 m      # yellow
ESC [ 44 m      # blue
ESC [ 45 m      # magenta
ESC [ 46 m      # cyan
ESC [ 47 m      # white
ESC [ 49 m      # reset
"""
from __future__ import print_function
#from builtins import str
from builtins import range
from builtins import object
import sys
# look for colorama https://pypi.python.org/pypi/colorama
from . import BaseCopySupporter, get_parameters


def have_colours(stream):
    """
    Detect if output console supports ANSI colors.

    :param stream:
    :return:
    """
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except BaseException:        # guess false in case of error
        return False


def formatter(format_string, kwargs):
    """
    Default formatter used to format strings. Instead of `"{key}".format(**kwargs)`
    use `formatter("{key}", kwargs)` which ensures that no errors are generated when
    an user uses braces e.g. {}. Bear in mind that formatter consumes kwargs
    which in turns replaces an used key with empty string "". This can generate
    unusual behaviour if not well used.
    """
    for key, val in kwargs.items():
        key2 = "{%s}" % (key)
        if key2 in format_string:
            # explicitly convert val to str
            format_string = format_string.replace(key2, str(val))
            kwargs[key] = ""
    return format_string


def separate(text):
    """
    Process a text to get its parts.

    :param text:
    :return: [head,body,end]
    """
    right = text.rstrip()
    left = text.lstrip()
    return (text[0:-len(left)], text[-len(left):len(right)], text[len(right):])


def scale(x, range, drange):
    """
    From real coordinates get rendered coordinates.

    :param x: source value
    :param range: (min,max) of x
    :param drange: (min,max) of sx
    :return: scaled x (sx)
    """
    (rx1, rx2) = float(range[0]), float(range[1])
    (sx1, sx2) = float(drange[0]), float(drange[1])
    return (sx2 - sx1) * (x - rx1) / (rx2 - rx1) + sx1


def scale_index(index, range, drange, circle=False, limit=False):
    """
    Uses scale but adds support for indexing.

    :param index:
    :param range:
    :param drange:
    :param circle:
    :param limit:
    :return:
    """
    minlen, maxlen = drange
    # (index - min) * maxlen / (max - min) # rescale to colors
    val = scale(index, range, drange)
    if val < 0:
        val -= 1  # shift negative
    index = int(val)  # get index
    # ensures that values are inside colors
    if index > maxlen - 1:
        if circle:
            index = index % (maxlen + minlen)
        elif limit:
            index = maxlen - 1
    if index < minlen:
        if circle:
            index = index % (-(maxlen - minlen))
        elif limit:
            index = minlen
    return index


class ANSIcolor(object):
    """
    Class defining ANSI color codes used in terminals
    """
    # INTENSITY
    BRIGHT = 1       # bright
    DIM = 2       # dim (looks same as normal brightness)
    NORMAL = 22    # normal brightness
    # FOREGROUND:
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [
        str(i) for i in range(30, 38)]
    # BACKGROUND
    BLACK_B, RED_B, GREEN_B, YELLOW_B, BLUE_B, MAGENTA_B, CYAN_B, WHITE_B = [
        str(i) for i in range(40, 48)]

    def __init__(self, colors):
        self.colors = ";".join(colors)
        self.format_code = "{_head}\x1b[{_colors}m{_body}\x1b[0m{_end}"

    def paint(self, *args, **kwargs):
        kwargs["_colors"] = self.colors
        if len(args) == 1:  # must have text
            kwargs["_head"], kwargs["_body"], kwargs["_end"] = separate(
                str(args[0]))
        elif len(args) > 1:  # format multiple
            return [self.paint(arg, **kwargs.copy()) for arg in args]
        return formatter(formatter(self.format_code, kwargs),
                         kwargs)  # formats for CODE and user masks

    __call__ = paint


class CODElist(list):
    """
    Especial list to hold CODE objects used in CodeMapper
    """

    def __init__(self, iterable):
        super(CODElist, self).__init__()
        self.extend(iterable)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def append(self, item):
        if not isinstance(item, CODE):
            raise TypeError('item is not of type %s' % CODE)
        for position, actualItem in enumerate(self):
            if item.level <= actualItem.level:
                super(CODElist, self).insert(position, item)
                return
        super(CODElist, self).append(item)


class CODE(BaseCopySupporter):
    """
    Class to define Logger codes like HIDDEN, DEBUG, ERROR, LOG, WARNING, IGNORE
    """

    def __init__(self, name=None, level=0, colors=None,
                 formatting="[{_code}]{_head}{_body}{_end}"):  # "[({_code}):{_head}{_body}{_end}]"): #
        """
        :param name: code name
        :param level: level of code priority
        :param colors: ANSIcolor instance
        :param formatting: formatting to use when converting text
        """
        self.name = name
        self.level = level
        if colors:
            colors = ANSIcolor(colors)
        self.colors = colors  # applied if color
        self.formatting = formatting  # applied if user defined
        self._use_color = have_colours(sys.stdout)
        self._buffer = None

    def convert(
            self,
            text,
            newLine=False,
            use_color=None,
            use_format=False,
            **kwargs):
        """
        Convert text to CODE format and colors.

        :param text: text to convert
        :param newLine: True to add new line at the end if needed
        :param use_color: True to use color
        :param use_format: True to use code formatting
        :param kwargs: additional kwargs to format
        :return: formatted text
        """
        if use_color is None:
            use_color = self._use_color

        if use_format:
            head, body, end = separate(text)
            kwargs = dict(_head=head, _body=body, _end=end, _name=self.name,
                          _level=self.level, _code=self.name, **kwargs)

            # formatter consumes kwargs!!
            # formats for CODE and user masks
            text = formatter(formatter(self.formatting, kwargs), kwargs)

        head, body, end = separate(text)
        if newLine and not end:
            end = "\n"

        if use_color and self.colors:  # if there are colors
            return self.colors(_head=head, _body=body, _end=end)
        else:
            return "{}{}{}".format(head, body, end)

    def codify(self, *args, **kwargs):
        """
        Creates an instance of this CODE with default parameters

        :param text: text to convert
        :param newLine: True to add new line at the end if needed
        :param use_color: True to use color
        :param use_format: True to use code formatting
        :param kwargs: additional kwargs to format
        :return: formatted text
        """
        code = self.clone()
        code._buffer = args, kwargs
        return code

    def raw_msg(self):
        if self._buffer is None:
            return ""  # return with no message
        else:
            kwargs = get_parameters(func=self.convert, args=self._buffer[0],
                                    kwargs=self._buffer[1], onlykeys=True,
                                    onlyused=True)
            kwargs["use_format"] = False
            kwargs["use_color"] = False
            return self.convert(**kwargs)

    def __str__(self):
        if self._buffer is None:
            return self.convert("")  # return with no message
        else:
            return self.convert(*self._buffer[0], **self._buffer[1])

    def __bool__(self):
        return True

    def __int__(self):
        return int(self.level)

    def __float__(self):
        return float(self.level)

    __call__ = codify


HIDDEN = CODE("HIDDEN", -3, (ANSIcolor.BLACK,))
DEBUG = CODE("DEBUG", -2, (ANSIcolor.CYAN,))
ERROR = CODE("ERROR", -1, (ANSIcolor.RED,))
LOG = CODE("LOG", 0, (ANSIcolor.BLUE,))
WARNING = CODE("WARNING", 1, (ANSIcolor.YELLOW,))
IGNORE = CODE("IGNORE", 2, (ANSIcolor.WHITE,))
OK = CODE("OK", 3, (ANSIcolor.GREEN,))

codes_list = CODElist([DEBUG, LOG, HIDDEN, WARNING, ERROR, IGNORE, OK])
codes_dict = {code.name: code for code in codes_list}


class CodeMapper(object):
    """
    Manage and convert CODE objects to other CODE objects
    """

    def __init__(self, codes=None, refcodes=None, range=None, limit=True):
        if codes:
            self.codes = codes
        else:
            self.codes = []
        self.refcodes = refcodes
        self.range = range
        self.limit = limit

    @property
    def codes(self):
        return self._codes

    @codes.setter
    def codes(self, values):
        if isinstance(values, CODElist):
            self._codes = values  # replace previous
        elif hasattr(values, "__iter__"):
            self._codes = CODElist(values)
        else:
            raise ValueError(
                "it only receives CODElist and converts iterators to CODElist")

    def map_code(self, code):
        """

        :param code:
        :return:
        """
        if isinstance(code, CODE):
            return self.get_by_reference(code)  # try by reference
        else:
            val = self.get_by_level(code)  # try by level
            if val:
                return val
            return self.get_by_index(code)  # try by index

    def get_by_index(self, index):
        """

        :param index:
        :return:
        """
        try:
            if self.range:  # scale values
                return self.codes[scale_index(index, self.range, (0, len(
                    self.codes)), limit=self.limit)]  # throws error when outside range
            else:
                return self.codes[scale_index(index, (0, len(self.codes)), (0, len(
                    self.codes)), limit=self.limit)]  # throws error when outside codes
        except TypeError as e:
            raise TypeError("{} is not an index".format(index))
        except IndexError as e:
            print(
                e,
                "{} exceeds codes dimensions. limit is {}, if True it selects the limit.".format(
                    index,
                    self.limit))

    def get_by_level(self, code):
        """

        :param code:
        :return:
        """
        for i in self.codes:
            if code == i.level:
                return i

    def get_by_reference(self, code):
        """

        :param code:
        :return:
        """
        refcodes = self.refcodes
        if refcodes:
            if code in refcodes:
                return refcodes[code]
        return code  # does nothing

    __call__ = map_code


class CodeLog(object):
    """
    Base Logger Class which supports CODE objects
    """
    use_colors = None
    use_codes = None

    def __init__(self, std_out=sys.stdout, code_mapper=None,
                 default_codes=None, use_colors=None, use_codes=None):
        """

        :param std_out: standard output
        :param code_mapper: object to map CODE objects
        :param default_codes:
        :param use_colors:
        :param use_codes:
        """
        # assigned from class
        if use_colors is None:
            use_colors = self.use_colors  # class default
        if use_codes is None:
            use_codes = self.use_codes  # class default
        # assigned from instance
        if use_colors is None:
            use_colors = have_colours(std_out)
        self.use_colors = use_colors
        if use_codes is None:
            use_codes = not self.use_colors  # if there is color do not use CODE
        self.use_codes = use_codes

        # control variables
        self.code_mapper = code_mapper
        self.std_out = std_out
        self.default_codes = default_codes

    @property
    def default_codes(self):
        return self._defcodes

    @default_codes.setter
    def default_codes(self, codes):
        if codes is not None and not hasattr(codes, "__iter__"):
            codes = [codes]
        self._defcodes = codes

    def convert_code(self, codes=None):
        """
        Filter accepted codes and adequate them to use.

        :param codes: levels, codes or iterators with them.
        :return: it gets None or list with only codes, no empty list (use if filtered)
        """
        if codes is None:  # use default
            return self.default_codes
        if not codes:  # use default
            return None
        if not hasattr(codes, "__iter__"):
            codes = [codes]  # it must be iterator
        if self.code_mapper:  # try to get code from color_mapper
            codes = [self.code_mapper(code)
                     for code in codes]  # some can be none
        codes = [
            code for code in codes if isinstance(
                code, CODE)]  # we need only codes
        if codes:  # empty list not printed but we want to print so use None codes
            return codes  # return list of codes else None

    def accepted_code(self, codes):
        """
        return True if codes is accepted else False
        """
        return bool(self.convert_code(codes=codes))

    def convert(self, text, codes=None, newLine=False, **kwargs):
        """
        Convert text with code.

        :param text: text to convert
        :param codes: codes to use for text
        :param newLine: True to add newline
        :param kwargs: additional arguments to pass to CODEs
        :return: string of formatted text
        """
        if isinstance(text, CODE):
            codes = self.convert_code(text)
            text = text.raw_msg()
        codes = self.convert_code(codes)
        if codes is None:  # print if None - no code used
            return str(text)  # ensures string
        else:  # empty list means that it was filtered
            useColor, useCODE = self.use_colors, self.use_codes
            lines = [str(code(text, newLine, useColor, useCODE, **kwargs))
                     for code in codes if code]
            return "".join(lines)

    def write(self, text, code=None, **kwargs):
        self.std_out.write(self.convert(text, code, **kwargs))
        self.std_out.flush()

    def printline(self, text, code=None, **kwargs):
        self.std_out.write(self.convert(text, code, True, **kwargs))
        self.std_out.flush()

    def printlines(self, lines, code=None, **kwargs):
        for line in lines:
            self.printline(line, code)

    __call__ = write


class EmptyLogger(CodeLog):
    """
    Empty logger to not generate outputs
    """

    def write(self, text, code=None, **kwargs):
        pass

    def printline(self, text, code=None, **kwargs):
        pass

    def printlines(self, lines, code=None, **kwargs):
        pass


class SimpleLogger(CodeLog):
    """
    Simple logger to print CODE objects
    """
    def __init__(self, std_out=sys.stdout, code_mapper=None, default_codes=LOG,
                 use_colors=None, use_codes=None, verbosity=None):
        """

        :param std_out:
        :param code_mapper:
        :param default_codes:
        :param verbosity: DEBUG = 0, LOG=1, HIDDEN=2, WARNING=3, ERROR=4
            if verbosity is None. it does not filter and lets any data to be logged.
            if verbosity is N it does not lets log those less than N.
            so if N = 2, it won't let log DEBUG and LOG levels but any other level is permitted.
            change self.states to add more levels that can be filtered with verbosity.
            Note that if self.states = () is is the same as verbosity = None.
        """
        if use_colors is None:
            use_colors = self.use_colors  # class inherited default
        if use_codes is None:
            use_codes = self.use_codes  # class inherited default
        super(
            SimpleLogger,
            self).__init__(
            std_out=std_out,
            code_mapper=code_mapper,
            default_codes=default_codes,
            use_colors=use_colors,
            use_codes=use_codes)
        self.verbosity = verbosity

    def convert_code(self, codes=None):
        """
        :param codes: levels, codes or iterators with them.
        :return: it gets None, list with only codes or empty list if filtered by verbosity
        """
        codes = super(SimpleLogger, self).convert_code(
            codes)  # it gets None or list with only codes
        if codes and self.verbosity is not None:  # verbosity is active and we got codes
            if hasattr(self.verbosity, "__iter__"):  # list of permitted codes
                codes = [
                    code for code in codes if float(code) in [
                        float(i) for i in self.verbosity]]
            else:  # verbosity is value or code
                codes = [
                    code for code in codes if float(code) >= float(
                        self.verbosity)]
        return codes  # let code live if None, we want to print it


class Loggers(object):
    """
    Manage multiple loggers
    """

    def __init__(self, logs=None, **kwargs):
        """
        :param logs: list of loggers
        :param kwargs: additional arguments to configure loggers
        """
        if logs:
            if hasattr(logs, "__iter__"):
                self.logs = logs
            else:
                raise Exception("logs must be a iterator")
        else:
            if kwargs:
                self.logs = [CodeLog]
            else:
                self.logs = [CodeLog()]
        if kwargs:
            for i, log in enumerate(self.logs):  # initialize all of them
                self.logs[i] = log(**kwargs)

    def post_setting(self, **kwargs):
        """
        Assign keyword arguments to logs.

        :param kwargs: keyword arguments
        """
        for log in self.logs:  # initialize all of them
            for name, value in kwargs.items():
                setattr(log, name, value)

    def write(self, text, state=None, **kwargs):
        for log in self.logs:
            log.write(text, state, **kwargs)

    def printline(self, text, state=None, **kwargs):
        for log in self.logs:
            log.printline(text, state, **kwargs)

    def printlines(self, lines, state=None, **kwargs):
        for log in self.logs:
            log.printlines(lines, state, **kwargs)


if __name__ == '__main__':

    c = SimpleLogger(default_codes=IGNORE, verbosity=(DEBUG, ERROR, IGNORE))

    c.printline(
        "\n\rthis is my debug message\r\n",
        DEBUG)  # no CR is appled after
    c.printline(" this is my warning message\r\n", WARNING)  # no CR is applied
    c.printline("this is my error message", ERROR)  # note that a CR is applied
    print("")
    # codes specifies which are printed with CODE object if not catch by
    # default_codes in the logger.
    cmap = CodeMapper(codes=(WARNING, ERROR))
    c.code_mapper = cmap  # you can use any function to return the desired CODE object
    cmap.range = 0, 10  # now all levels are mapped to codes in that range

    def printer(msg, it=10):
        for level in range(-it, it):
            c.printline(msg, level, it=level)
            sys.stdout.write(c.convert("this is normal text", None, True))
    printer(
        "\r\nthis it a text with mapped level {it} to level {_level} that represents -> {_code}\r\n")

    lgs = Loggers()
    lgs.logs.append(c)
    lgs.printline("logging with several loggers")
    lgs.printline("and testing that Warning should not appear in one", WARNING)

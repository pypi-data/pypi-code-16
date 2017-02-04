"""Extract, format and print information about Python stack traces."""

import re
import sys
import types
import inspect
import linecache
import collections

__all__ = ['extract_stack', 'extract_tb', 'format_exception',
           'format_exception_only', 'format_list', 'format_stack',
           'format_tb', 'print_exc', 'format_exc', 'print_exception',
           'print_last', 'print_stack', 'print_tb', 'tb_modeno']

__version__ = '0.1.1'

def _print(file, str='', terminator='\n'):
    file.write(str+terminator)

def print_list(extracted_list, file=None, tb_mode='compact'):
    """Print the list of tuples as returned by extract_tb() or
    extract_stack() as a formatted stack trace to the given file."""
    if file is None:
        file = sys.stderr
    lst = format_list(extracted_list, tb_mode)
    _print(file, "".join(lst))

_MaxParamLength = 25
def _format_value(value):
    """
    Format a value into a printable form

    :param value: anything really
    :returns: a string representation of value, usually repr(value)
    """
    # Make prettyargs prettier by removing extra verbiage and addresses
    # pylint: disable=invalid-name
    s = re.sub('<(.+?) at .*?>', lambda m: '<%s>' % m.group(1), repr(value))
    if len(s) > _MaxParamLength:
        s = s[:_MaxParamLength/2] + '......' + s[-_MaxParamLength/2:]
    return '=' + s

def _format_args(frame):
    """
    Extract and format function/method parameters from frame.

    :param frame: Frame object
    :returns: string representing function args, like 'a=5, b=0'
    """
    (args, varargs, varkw, frame_locals) = inspect.getargvalues(frame)
    try:
        prettyargs = inspect.formatargvalues(args, varargs, varkw, frame_locals,
                                             formatvalue=_format_value)
    except Exception as e:
        prettyargs = '(?)'
    return prettyargs

def _format_compressed_line(extracted_line):
    filename, lineno, name, line = extracted_line[:4]
    line = ': %s' % line if line else ''
    if len(filename) > 30:
        filename = '[...]' + filename[-25:]
    return '  %s, %s, %d%s\n' % (filename, name, lineno, line)

def _format_compact_line(extracted_line):
    filename, lineno, name, line = extracted_line[:4]
    line = ': %s' % line if line else ''
    return '  File "%s", in %s at line %d%s\n' % (filename, name, lineno, line)

def _format_line(extracted_line):
    filename, lineno, name, line = extracted_line[:4]
    item = '  File "%s", line %d, in %s\n' % (filename,lineno,name)
    if line:
        item += '    %s\n' % line.strip()
    return item

_FMT_LINE_MAP = collections.defaultdict(lambda : _format_line, {
    'compressed': _format_compressed_line,
    'compact': _format_compact_line,
})

def format_list(extracted_list, tb_mode='compact'):
    """Format a list of traceback entry tuples for printing.

    Given a list of tuples as returned by extract_tb() or
    extract_stack(), return a list of strings ready for printing.
    Each string in the resulting list corresponds to the item with the
    same index in the argument list.  Each string ends in a newline;
    the strings may contain internal newlines as well, for those items
    whose source text line is not None.
    """
    fmt_line = _FMT_LINE_MAP[tb_mode]
    return [fmt_line(line) for line in extracted_list]

def print_tb(tb, limit=None, file=None):
    """Print up to 'limit' stack trace entries from the traceback 'tb'.

    If 'limit' is omitted or None, all entries are printed.  If 'file'
    is omitted or None, the output goes to sys.stderr; otherwise
    'file' should be an open file or file-like object with a write()
    method.
    """
    if file is None:
        file = sys.stderr
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        _print(file,
               '  File "%s", line %d, in %s' % (filename, lineno, name))
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line: _print(file, '    ' + line.strip())
        tb = tb.tb_next
        n = n+1

def format_tb(tb, limit = None, tb_mode='compact', show_args=False):
    """A shorthand for 'format_list(extract_tb(tb, limit))'."""
    return format_list(extract_tb(tb, limit, show_args), tb_mode)

def extract_tb(tb, limit = None, show_args=False):
    """Return list of up to limit pre-processed entries from traceback.

    This is useful for alternate formatting of stack traces.  If
    'limit' is omitted or None, all entries are extracted.  A
    pre-processed stack trace entry is a quadruple (filename, line
    number, function name, text) representing the information that is
    usually printed for a stack trace.  The text is a string with
    leading and trailing whitespace stripped; if the source is not
    available it is None.
    """
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        if show_args:
            name += _format_args(f)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line: line = line.strip()
        else: line = None
        list.append((filename, lineno, name, line))
        tb = tb.tb_next
        n = n+1
    return list


def print_exception(etype, value, tb, limit=None, file=None, tb_mode='compact', show_args=False):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    if file is None:
        file = sys.stderr
    _print(file, "".join(format_exception(etype, value, tb, limit=limit,
                                          tb_mode=tb_mode, show_args=show_args)))

def format_exception(etype, value, tb, limit = None, tb_mode='compact', show_args=False):
    """Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The return value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().
    """
    if tb:
        list = ['Traceback (most recent call last):\n']
        list = list + format_tb(tb, limit, tb_mode, show_args=show_args)
    else:
        list = []
    list = list + format_exception_only(etype, value)
    return list

def format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """

    # An instance should not have a meaningful value parameter, but
    # sometimes does, particularly for string exceptions, such as
    # >>> raise string1, string2  # deprecated
    #
    # Clear these out first because issubtype(string1, SyntaxError)
    # would raise another exception and mask the original problem.
    if (isinstance(etype, BaseException) or
        isinstance(etype, types.InstanceType) or
        etype is None or type(etype) is str):
        return [_format_final_exc_line(etype, value)]

    stype = etype.__name__

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    try:
        msg, (filename, lineno, offset, badline) = value.args
    except Exception:
        pass
    else:
        filename = filename or "<string>"
        lines.append('  File "%s", line %d\n' % (filename, lineno))
        if badline is not None:
            lines.append('    %s\n' % badline.strip())
            if offset is not None:
                caretspace = badline.rstrip('\n')
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept for alignment
                caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                lines.append('    %s^\n' % ''.join(caretspace))
        value = msg

    lines.append(_format_final_exc_line(stype, value))
    return lines

def _format_final_exc_line(etype, value):
    """Return a list of a single line -- normal case for format_exception_only"""
    valuestr = _some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = "%s: %s\n" % (etype, valuestr)
    return line

def _some_str(value):
    try:
        return str(value)
    except Exception:
        pass
    try:
        value = unicode(value)
        return value.encode("ascii", "backslashreplace")
    except Exception:
        pass
    return '<unprintable %s object>' % type(value).__name__


def print_exc(limit=None, file=None, tb_mode='compact', show_args=False):
    """Shorthand for 'print_exception(sys.exc_type, sys.exc_value, sys.exc_traceback, limit, file)'.
    (In fact, it uses sys.exc_info() to retrieve the same information
    in a thread-safe way.)"""
    if file is None:
        file = sys.stderr
    try:
        etype, value, tb = sys.exc_info()
        print_exception(etype, value, tb, limit, file, tb_mode, show_args)
    finally:
        etype = value = tb = None


def format_exc(limit=None, tb_mode='compact', show_args=False):
    """Like print_exc() but return a string."""
    try:
        etype, value, tb = sys.exc_info()
        return ''.join(format_exception(etype, value, tb, limit, tb_mode, show_args))
    finally:
        etype = value = tb = None


def print_last(limit=None, file=None, tb_mode='compact', show_args=False):
    """This is a shorthand for 'print_exception(sys.last_type,
    sys.last_value, sys.last_traceback, limit, file)'."""
    if not hasattr(sys, "last_type"):
        raise ValueError("no last exception")
    if file is None:
        file = sys.stderr
    print_exception(sys.last_type, sys.last_value, sys.last_traceback,
                    limit, file, tb_mode, show_args)


def print_stack(f=None, limit=None, file=None, tb_mode='compact', show_args=False):
    """Print a stack trace from its invocation point.

    The optional 'f' argument can be used to specify an alternate
    stack frame at which to start. The optional 'limit' and 'file'
    arguments have the same meaning as for print_exception().
    """
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    print_list(extract_stack(f, limit, show_args), file, tb_mode)

def format_stack(f=None, limit=None, tb_mode='compact', show_args=False):
    """Shorthand for 'format_list(extract_stack(f, limit))'."""
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    return format_list(extract_stack(f, limit, show_args), tb_mode)

def extract_stack(f=None, limit = None, show_args=False):
    """Extract the raw traceback from the current stack frame.

    The return value has the same format as for extract_tb().  The
    optional 'f' and 'limit' arguments have the same meaning as for
    print_stack().  Each item in the list is a quadruple (filename,
    line number, function name, text), and the entries are in order
    from oldest to newest stack frame.
    """
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while f is not None and (limit is None or n < limit):
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        if show_args:
            name += _format_args(f)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line: line = line.strip()
        else: line = None
        list.append((filename, lineno, name, line))
        f = f.f_back
        n = n+1
    list.reverse()
    return list

def tb_lineno(tb):
    """Calculate correct line number of traceback given in tb.

    Obsolete in 2.3.
    """
    return tb.tb_lineno

def monkey_patch(**options):
    import traceback
    from functools import partial
    traceback = options.pop('module', traceback)
    partial = partial(partial, **options)
    traceback.format_list = partial(format_list)
    traceback.format_stack = partial(format_stack)
    traceback.format_tb = partial(format_tb)
    traceback.format_exc = partial(format_exc)
    traceback.format_exception = partial(format_exception)
    traceback.print_list = partial(print_list)
    traceback.print_stack = partial(print_stack)
    traceback.print_last = partial(print_last)
    traceback.print_exc = partial(print_exc)
    traceback.print_exception = partial(print_exception)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from collections import namedtuple
from tempfile import SpooledTemporaryFile

__version__ = '0.0.8'


def escape_output(s):
    """ Escape output using python's repr(). """
    return repr(s)[1:-1]


class ProcessOutput(object):
    """ Uses subprocess to run a process and stores all stdout/stderr
        output as bytes.
        The ProcessOutput object can be used as a context manager, or the
        run() method must be called after inititalization.
        Output is stored in self.stdout and self.stderr as bytes.
        The output must be decoded.


        NOTE:
            As of Python 3.4+, you can use:
                subprocess.check_output(input=b'test')`
            or:
                `subprocess.run(..., input=b'test')`
            ..for simple cases.
            ProcessOutput can still be useful for programs that output both
            `stdout` and `stderr` though.

    """
    # Holds data returned by ProcessOutput.proc_output()
    ProcOutput = namedtuple('ProcOutput', ('stdout', 'stderr'))

    def __init__(self, args, stdin_data=None, timeout=None, **popenkwargs):
        """ Initialize a ProcessOutput object to be used as a context manager,
            or by calling self.run() afterwards.
            Arguments:
                args           : Command arguments, same as subprocess.Popen.
                stdin_data     : str or bytes to send to command as stdin.
                timeout        : Time to wait for process after collecting
                                 the output.
                **popenkwargs  : Any extra kwargs for Popen().
        """
        self.proc = None
        self.pid = None
        self.returncode = None
        self.timeout = timeout
        self.stdout = b''
        self.stderr = b''
        self.args = args
        self.stdin_data = stdin_data
        self.popenkwargs = popenkwargs

    def __enter__(self):
        self.stdout = b''
        self.stderr = b''
        self.run()
        return self

    def __exit__(self, exctype, value, traceback):
        return False

    def _iter_proc_output(self, stream):
        """ Iterate over proc.stdout or proc.stderr, yielding lines. """
        if not hasattr(stream, 'readline'):
            raise TypeError(
                'Expecting a file with a readline method. Got: {}'.format(
                    type(stream).__name__
                )
            )
        for line in iter(stream.readline, b''):
            if line:
                yield line.rstrip(b'\n')
            else:
                break

    def _run(self):
        """ Run the command, and set instance attribute values like self.proc.
        """
        if self.stdin_data is None:
            stdin_file = None
        else:
            stdin_file = TempStdinInput(self.stdin_data)

        # These keyword arguments cannot be changed by the user.
        popenkwargs = {k: v for k, v in self.popenkwargs.items()}
        popenkwargs.update({
            'stdin': None if stdin_file is None else stdin_file.open(),
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        })

        self.proc = subprocess.Popen(self.args, **popenkwargs)
        self.pid = self.proc.pid
        if stdin_file is not None:
            stdin_file.close()

    def iter_stderr(self):
        """ Calls `_run()`, and yields stderr lines as they are received. """
        self._run()
        for line in self._iter_proc_output(self.proc.stderr):
            yield line

    def iter_stdout(self):
        """ Calls `_run()`, and yields stdout lines as they are received. """
        self._run()
        for line in self._iter_proc_output(self.proc.stdout):
            yield line

    def proc_output(self, proc):
        """ Get process output, whether its on stdout or stderr.
            Returns a named tuple of strings,
            ProcOutput(stdout_output, stderr_output).

            Arguments:
                proc  : a POpen() process to get output from.
        """
        return self.ProcOutput(
            b'\n'.join(self._iter_proc_output(proc.stdout)),
            b'\n'.join(self._iter_proc_output(proc.stderr))
        )

    def run(self, timeout=None):
        """ Run the command specified during init, and set self.stdout/stderr.
            A ProcOutput (namedtuple) is returned with
            (stdout_data, stderr_data) stored as bytes.
            The output must be decoded (same as subprocess).
        """
        self._run()
        procoutput = self.proc_output(self.proc)
        self.stdout, self.stderr = procoutput
        self.returncode = self.proc.wait(timeout=timeout or self.timeout)

        return procoutput


class StdOutCatcher(object):
    """ Catches stdout for code inside the 'with' block.

        Usage:
            with StdOutCatcher(safe=True, maxlength=160) as fakestdout:
                # stdout is stored in fakestdout.output
                print('okay')
            # stdout is back to normal
            # retrieve the captured output..
            print('output was: {}'.format(fakestdout.output))
    """
    def __init__(self, escaped=False, max_length=0):
        # Use safe_output?
        self.escaped = escaped
        # Maximum length before trimming output
        self.max_length = max_length
        # Output
        self._output = ''
        self.length = 0
        self.max_exceeded = False

    def __enter__(self):
        # Replace fileobj with self, fileobj.write() will be self.write()
        sys.stdout = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stdout.
        sys.stdout = sys.__stdout__
        return False

    def flush(self):
        """ Doesn't do anything, but it's here for compatibility. """
        return None

    @property
    def name(self):
        return getattr(
            sys.stdout,
            'name',
            getattr(sys.stdout, '__name__', type(sys.stdout).__name__)
        )

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        """ Sets self._output, escaping first if self.escaped is truthy. """
        if self.escaped:
            self._output = escape_output(value)
            return None
        self._output = value
        return None

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError('write() expects a str, got: {}'.format(
                type(s).__name__
            ))
        if (not s) or self.max_exceeded:
            # Nothing to write, or max-length was already exceeded.
            return 0

        # Save output
        self.output = ''.join((
            self.output,
            s
        ))
        # Trim and block the next call if we are already at max_length.
        if (self.max_length > 0) and len(self.output) >= self.max_length:
            self.output = self.output[:self.max_length]
            self.max_exceeded = True
        # Output length may have been trimmed.
        self.length = len(self.output)
        return len(s)


class StdErrCatcher(StdOutCatcher):
    def __enter__(self):
        # Replace stderr with self, stderr.write() will be self.write()
        sys.stderr = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stderr.
        sys.stderr = sys.__stderr__
        return False

    @property
    def name(self):
        return getattr(
            sys.stderr,
            'name',
            getattr(sys.stderr, '__name__', type(sys.stderr).__name__)
        )


class TempStdinInput(object):
    """ Creates a file-like object from a string, to be used as stdin
        input for ProcessOutput().
    """
    def __init__(self, data):
        self.tempfile = SpooledTemporaryFile()
        # Write data to our file, then seek back to 0 for reading.
        self.tempfile.write(data.encode() if isinstance(data, str) else data)
        self.tempfile.seek(0)

    def __enter__(self):
        return self.tempfile

    def __exit__(self, exctype, value, traceback):
        self.close()
        return False

    def close(self):
        self.tempfile.close()

    def open(self):
        # It's already open.
        return self.tempfile

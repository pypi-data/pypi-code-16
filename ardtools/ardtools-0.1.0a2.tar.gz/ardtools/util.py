"""
Utility routines.
"""

# standard library imports
import sys
import os
import argparse
import pwd
import subprocess
import pipes
import paramiko

# package specific imports
import __main__ as main
from version import get_package_version_str

########################################################################
# Atributes
########################################################################
__author__ = "Alan Staniforth <devops@erehwon.xyz>"
__copyright__ = "Copyright (c) 2004-2016 Alan Staniforth"
__license__ = "New-style BSD"
__version__ = get_package_version_str()


########################################################################
# Interface
########################################################################
__all__ = [
            # Classes
            'PlainHelpFormatter', 'switch', 'CommandAction',
            # Functions
            'ensure_dir', 'get_script_name', 'get_cur_username',
            'is_root', 'get_real_username', 'extend_tuple', 'exec_cli',
            'report_exec_cli_result'
            ]


########################################################################
# Classes
########################################################################

class PlainHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Class to improve formatting of optparse help output

    Helper class for op, tell your OptionParser to use this to format
    the help text when first instantiate the object. Thus:

    parser = OptionParser(..., formatter=ptl.PlainHelpFormatter(), ...)
    """
    def format_description(self, description):
        if description:
            return description + "\n"
        else:
            return ""


class switch(object):
    """
    Class to implement switch statement in Python.

    From <http://code.activestate.com/recipes/410692/>

    Simple example:

        v = 'ten'
        for case in switch(v):
            if case('one'):
                print 1
                break
            if case('two'):
                print 2
                break
            if case('ten'):
                print 10
                break
            if case('eleven'):
                print 11
                break
            if case(): # default, could also just omit condition or 'if True'
                print "something else!"
                # No need to break here, it'll stop anyway
    """
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class CommandAction(argparse.Action):
    """
    Clever trick to place a positional argument anywhere in the command line.

    Based on an idea from Stack Overflow:

    <http://stackoverflow.com/a/5374229>

    """
    def __call__(self, parser, namespace, values, option_string=None):

        setattr(namespace, 'command', values[0])


class CommandAction(argparse.Action):
    """
    Clever trick to place a positional argument anywhere in the command line.
    
    Based on an idea from Stack Overflow:
    
    <http://stackoverflow.com/a/5374229>
    
    """
    def __call__(self, parser, namespace, values, option_string=None):

        setattr(namespace, 'command', values[0])


########################################################################
# Functions
########################################################################

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    Thanks to Aaron Hall <http://stackoverflow.com/a/26853961> for this
    method that is portable across Python 2 and 3. Aaron also gives the
    way to do this if you can guarantee Python 3: z = (**x, **y).

    Params:
        *dict_args -
        debug - if True output debugging info

    Returns:
        The merged dictionaries with later key:value pair having precedence
            over earlier
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def extend_tuple(in_tuple, deep, value_only, *new):
    """
    Add item(s) to a tuple

    Params:
        in_tuple:   The tuple to be extended

        deep:       If the item(s) in new is an iterable item (list, tuple
                    dict) then add the contents as individual items of the
                    new tuple. The method does not regard strings as iterable.

                    This does not cause the function to recurse into contained
                    container objects, ie if the list [1, [2, 3, 4], 5] is
                    passed, the items added will be 1, [2, 3, 4] and 5, not
                    1, 2, 3, 4, 5.

        value_only: If deep is true and the object being iterated is a dict
                    then by default the items will be added as tuples of each
                    key/value pair. If this is True then the bare value only
                    will be added.

        new:        The item (or items) to add.

    Returns:
        A tuple with the new item(s)

    """
    new_tuple_list = []
    for i in in_tuple:
        new_tuple_list.append(i)
    for arg in new:
        if deep:
            if hasattr(arg, '__iter__'):
                # special case for dicts
                if type(arg) is dict:
                    for i in arg:
                        if value_only:
                            new_tuple_list.append(arg[i])
                        else:
                            new_tuple_list.append((i, arg[i]))
                else:
                    for i in arg:
                        new_tuple_list.append(i)
            else:
                new_tuple_list.append(arg)
        else:
            new_tuple_list.append(arg)
    return tuple(new_tuple_list)


def ensure_dir(f, fake_it=False):
    """
    Ensures the directory holding the file passed in exists - by creating it
    and any required enclosing directory if necessary

    Params:
        f: the file path whose directory is to be created if not present
        fake_it: if true don't create dir, just print a log line

    Returns:
        If nothing is done: False
        If a directory is created: True

    """
    d = os.path.dirname(os.path.abspath(f))
    dir_created = False
    if not os.path.exists(d):
        dir_created = True
        # print "Creating missing '" + d + "' directory"
        if not fake_it:
            # only actually create dirs if not testing
            try:
                os.makedirs(d, 0755)
            except:
                dir_created = False
    return dir_created


def split_path(in_path, debug=False):
    """
    Platform independant method to split a file path into its components

    The function does no path expansion or conversion. If you pass a partial
    path the returned array will only conjtain the parts of the path in that
    partial path and if (on windows) there is no drive specifier no drive
    letter will be returned.

    Params:
        in_path - the path to parse as a string
        debug - if True output debugging info

    Returns a tuple whose parts are:
        [0] - the drive letter if (a) on Windows and (b) if present in the
              path, otherwise ''
        [1] - an array, each element a path component
    """
    drive, path = os.path.splitdrive(in_path)
    parts = []
    while True:
        newpath, tail = os.path.split(path)
        if debug:
            print repr(path), (newpath, tail)
        if newpath == path:
            assert not tail
            if path:
                parts.append(path)
            break
        parts.append(tail)
        path = newpath
    parts.reverse()
    return (drive, parts)


def get_script_name():
    """Returns the stripped name of the script file that called the function"""
    s_name = os.path.basename(main.__file__)
    return s_name


def is_root():
    """Check if running as root."""
    cur_user_name = get_cur_username()
    return cur_user_name == 'root'


def get_cur_username():
    """Get the current user name."""
    return(pwd.getpwuid(os.getuid())[0])


def get_real_username():
    """Get the real login user name, even if deep in a sudo"""
    return(exec_cli(['logname'])[0].strip())


def cmd_line_from_list(in_list):
    """
    Takes a list of strings, each representing one item of a POSIX command
    line, and returns them combined into a single string correctly quoted
    so it could be pasted into a terminal or executed via os.system() or
    paramiko.
    """
    out_string = ' '.join(pipes.quote(p) for p in in_list)
    return out_string


def exec_cli(command_list, fake_it=False, host=None, user=None, echo=False):
    """
    Construct and execute a command line, either locally or on a remote host.

    Params:
        command_list:   list of strings to be passed to subprocess.check_call()
        fake_it:        if true don't create dir, just print a log line
        remote_host:    the remote host on which to execute the command
        echo:           print the command output

    If command is to executed on a remote host paramiko will be used and the
    assumption made that an SSH key is loaded in ssh_agent that will allow
    the paramiko ssh client to log in without a password.

    Returns: the output in response to the command - or None
             the std error output in response tot he command - or None
             the command return code - or None

             as a tuple: (raw_output, raw_err, ret_code)
    """
    raw_output = raw_err = ret_code = None
    if not fake_it:
        try:
            if host is None:
                my_proc = subprocess.Popen(command_list,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                (raw_output, raw_err) = my_proc.communicate()
                ret_code = my_proc.returncode
            else:
                # paramiko.util.log_to_file('ssh.log') # sets up logging
                BUF_SIZE = -1
                cmd = cmd_line_from_list(command_list)
                cmd = cmd.encode('utf-8')
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.connect(host, username=user)
                chan = client.get_transport().open_session()
                chan.exec_command(cmd)
                raw_output = ''.join(chan.makefile('rb', BUF_SIZE))
                raw_err = ''.join(chan.makefile_stderr('rb', BUF_SIZE))
                ret_code = chan.recv_exit_status()
                client.close()
        except subprocess.CalledProcessError, e:
            if raw_err is None:
                raw_err = ""
            print "Command '" + " ".join(command_list) + \
                  "' failed, error: " + str(e.returncode) + ': ' + raw_err
        except (paramiko.SSHException, paramiko.PasswordRequiredException,
                paramiko.BadAuthenticationType, paramiko.ChannelException,
                paramiko.BadHostKeyException, paramiko.AuthenticationException,
                paramiko.ProxyCommandFailure) as e:
            if raw_err is None:
                raw_err = ""
            print "Paramiko command '" + " ".join(command_list) + \
                  "' failed, error: " + e.message + ': ' + raw_err
            if client is not None:
                client.close()
        except:
            if raw_err is None:
                raw_err = ""
            print "Unexpected error:", sys.exc_info()[0], ': ', raw_err
    else:
        print " ".join(command_list)
    if echo:
        if (raw_output is not None) and (raw_output is not ""):
            print raw_output
        if (raw_err is not None) and (raw_err is not ""):
            print raw_err
    return (raw_output, raw_err, ret_code)


def run_applescript(script, fake_it=False):
    """
    Runs an Applescript.

    Params:
        script: a list, each item of which is a line of the Applescript
        fake_it: if true don't create dir, just print a log line
    """
    osascript_command = ['osascript']  # Initialise the osascript command line
    for script_line in script:
        # Add each line of the script to the osascript command line
        osascript_command.append('-e')
        osascript_command.append(script_line)
    if not fake_it:
        try:
            subprocess.check_call(osascript_command)
        except subprocess.CalledProcessError, e:
            print "Command '" + " ".join(osascript_command) + \
                  "' failed, error: " + str(e.returncode)
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            pass
    else:
        print " ".join(osascript_command)

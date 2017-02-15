import logging
import re
from textwrap import dedent

from .tecutil import _tecutil, lock
from .exception import TecplotLogicError, TecplotMacroError

log = logging.getLogger(__name__)


@lock()
def execute_command(cmd):
    """Runs a series of tecplot macro commands.

    Parameters:
        cmd (`string <str>`): The macro commands to be run.

    Raises:
        `TecplotMacroError`: Message will specify the command that failed.

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    This command splits the input into individual commands and runs them one
    at a time. See the |Tecplot Macro Scripting Guide| for details about
    |Tecplot 360 EX|'s macro language.

    .. warning::
        Currently, only commands that do not require raw data, by use of the
        ``RAWDATA`` macro directive, are accepted.

    .. warning::
        Intrinsic variables (that is, variables with pipes such as
        ``|DATASETFNAME|``) are not supported. If you need to use an intrinsic
        variable in the macro command, add the macro command to a text file and
        call `execute_file`.

    See the |Tecplot Macro Scripting Guide| for more information about raw data
    and intrinsic variables.

    The following command will perform the same operations as the
    `Hello, World! example <hello_world>`::

        >>> tecplot.macro.execute_command(r'''
        ...   $!ATTACHTEXT
        ...     ANCHORPOS { X = 35 Y = 50 }
        ...     TEXTSHAPE { HEIGHT = 35 }
        ...     TEXT = 'Hello, World!'
        ...   $!EXPORTSETUP EXPORTFNAME = 'hello_world.png'
        ...   $!EXPORT
        ...     EXPORTREGION = CURRENTFRAME
        ... ''')
    """
    cmts = re.compile(r'(?<!\\)(\".*?\"|\'.*?\')|(#[^\r\n]*$)', re.MULTILINE)
    ptrn = re.compile(r'(\$!.*?)(?=\$!)|(\$!.*)', re.MULTILINE | re.DOTALL)
    cmd = cmts.sub(lambda m: m.group(1) or '', cmd)
    for match in ptrn.finditer(cmd):
        c = (match.group(1) or match.group(2)).strip()
        if __debug__:
            log.debug('executing command:\n' + c)
        try:
            if not _tecutil.MacroExecuteCommand(c):
                raise TecplotMacroError(c)
        except TecplotLogicError as e:
            raise TecplotMacroError()


def execute_extended_command(procid, cmd):
    """Runs a tecplot macro command defined in an addon.

    Parameters:
        procid (`string <str>`): Registered name of the addon.
        cmd (`string <str>`): The command to run.

    Raises:
        `TecplotMacroError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    In general, the command string is formatted prior to being fed into the
    |Tecplot Engine| so liberal use of whitespace, including new-lines, are
    acceptable.

    Example::

        >>> tecplot.macro.execute_extended_command(
        ...     'Multi Frame Manager',
        ...     'TILEFRAMESSQUARE')
    """
    cmd = dedent('''
            $!EXTENDEDCOMMAND
              COMMANDPROCESSORID = '{procid}'
              COMMAND = '{cmd}'
        '''.format(procid=procid,
                   cmd=' '.join(cmd. split()).replace(r"'", r"\'")))
    execute_command(cmd)


@lock()
def execute_file(filename):
    """Run a macro file.

    Parameters:
        filename (`string <str>`): The file to be run.

    Raises:
        `TecplotMacroError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    Example::

        >>> tecplot.macro.execute_file('/path/to/macro_file.mcr')
    """
    try:
        if not _tecutil.MacroRunFile(filename):
            raise TecplotMacroError(filename)
    except TecplotLogicError as e:
        raise TecplotMacroError(str(e))

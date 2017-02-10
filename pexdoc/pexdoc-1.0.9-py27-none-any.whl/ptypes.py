# ptypes.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0916

# Standard library imports
import os
import platform
import inspect
# Intra-package imports
import pexdoc.pcontracts


###
# Functions
###
def _normalize_windows_fname(fname, _force=False):  # pragma: no cover
    """
    Function copied from pmisc module to avoid
    import loops
    """
    if ((platform.system().lower() != 'windows')
       and (not _force)):   # pragma: no cover
        return fname
    # Replace unintended escape sequences that could be in
    # the file name, like "C:\appdata"
    rchars = {
        '\x07': r'\\a',
        '\x08': r'\\b',
        '\x0C': r'\\f',
        '\x0A': r'\\n',
        '\x0D': r'\\r',
        '\x09': r'\\t',
        '\x0B': r'\\v',
    }
    ret = ''
    for char in os.path.normpath(fname):
        ret = ret+rchars.get(char, char)
    # Remove superfluous double backslashes
    network_share = False
    tmp = None
    while tmp != ret:
        tmp, ret = ret, ret.replace('\\\\', '\\')
        if ret.startswith(r'\\') and (len(ret) > 2) and (ret[2] != r'\\'):
            network_share = True
    ret = ret.replace('\\\\', '\\')
    # Put back network share if needed
    if network_share:
        ret = r'\\'+ret.lstrip(r'\\')
    return ret


@pexdoc.pcontracts.new_contract()
def file_name(obj):
    r"""
    Validates if an object is a legal name for a file
    (i.e. does not have extraneous characters, etc.)

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not
     valid). The token \*[argument_name]\* is replaced by the name
     of the argument the contract is attached to

    :rtype: None
    """
    msg = pexdoc.pcontracts.get_exdesc()
    # Check that argument is a string
    if ((not isinstance(obj, str) or
       (isinstance(obj, str) and ('\0' in obj)))):
        raise ValueError(msg)
    # If file exists, argument is a valid file name, otherwise test
    # if file can be created. User may not have permission to
    # write file, but call to os.access should not fail if the file
    # name is correct
    try:
        if not os.path.exists(obj):
            os.access(obj, os.W_OK)
    except (TypeError, ValueError): # pragma: no cover
        raise ValueError(msg)


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    file_not_found=(OSError, 'File *[fname]* could not be found')
)
def file_name_exists(obj):
    r"""
    Validates if an object is a legal name for a file
    (i.e. does not have extraneous characters, etc.) *and* that the
    file exists

    :param obj: Object
    :type  obj: any

    :raises:
     * OSError (File *[fname]* could not be found). The
       token \*[fname]\* is replaced by the *value* of the
       argument the contract is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not valid).
       The token \*[argument_name]\* is replaced by the name of
       the argument the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    msg = exdesc['argument_invalid']
    # Check that argument is a string
    if ((not isinstance(obj, str) or
       (isinstance(obj, str) and ('\0' in obj)))):
        raise ValueError(msg)
    # Check that file name is valid
    try:
        os.path.exists(obj)
    except (TypeError, ValueError): # pragma: no cover
        raise ValueError(msg)
    # Check that file exists
    obj = _normalize_windows_fname(obj)
    if not os.path.exists(obj):
        msg = exdesc['file_not_found']
        raise ValueError(msg)


@pexdoc.pcontracts.new_contract()
def function(obj):
    r"""
    Validates if an object is a function pointer or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if (obj is None) or inspect.isfunction(obj):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def non_negative_integer(obj):
    r"""
    Validates if an object is a non-negative (zero or positive) integer

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    if isinstance(obj, int) and (not isinstance(obj, bool)) and (obj >= 0):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def non_null_string(obj):
    r"""
    Validates if an object is a non-null string

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    if isinstance(obj, str) and (len(obj) > 0):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def offset_range(obj):
    r"""
    Validates if an object is a number in the [0, 1] range

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((isinstance(obj, int) or isinstance(obj, float)) and
       (not isinstance(obj, bool)) and (obj >= 0) and (obj <= 1)):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def positive_real_num(obj):
    r"""
    Validates if an object is a positive integer, positive float
    or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((obj is None) or ((isinstance(obj, int) or
       isinstance(obj, float)) and (obj > 0) and (not isinstance(obj, bool)))):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def real_num(obj):
    r"""
    Validates if an object is an integer, float or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((obj is None) or
       ((isinstance(obj, int) or isinstance(obj, float)) and
       (not isinstance(obj, bool)))):
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())

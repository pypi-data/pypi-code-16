# doccode.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E1129,R0914,R0915,W0212,W0640

# Standard library imports
from __future__ import print_function
import os
import subprocess
import sys
# PyPI imports
import pmisc
from pmisc import AE
# Intra-package imports
import pexdoc.pcontracts


###
# Functions
###
def test_exdoc_doccode():
    """ Test code used in exdoc module """
    def remove_header(stdout):
        """ Remove py.test header """
        actual_text = []
        off_header = False
        lines = (
            stdout.split('\n')
            if sys.hexversion < 0x03000000 else
            stdout.decode('ascii').split('\n')
        )
        for line in lines:
            off_header = line.startswith('Callable:') or off_header
            if off_header:
                actual_text.append(line)
        return '\n'.join(actual_text)
    # Test tracing module #1 (py.test based)
    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'docs',
        'support'
    )
    script_name = os.path.join(script_dir, 'trace_my_module_1.py')
    proc = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    actual_text = remove_header(stdout)
    ref_list = []
    ref_list.append('Callable: docs.support.my_module.func')
    ref_list.append('.. Auto-generated exceptions documentation for')
    ref_list.append('.. docs.support.my_module.func')
    ref_list.append('')
    ref_list.append(':raises: TypeError (Argument \\`name\\` is not valid)')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('Callable: docs.support.my_module.MyClass.value')
    ref_list.append('.. Auto-generated exceptions documentation for')
    ref_list.append('.. docs.support.my_module.MyClass.value')
    ref_list.append('')
    ref_list.append(':raises:')
    ref_list.append(' * When assigned')
    ref_list.append('')
    ref_list.append('   * RuntimeError (Argument \\`value\\` is not valid)')
    ref_list.append('')
    ref_list.append(' * When retrieved')
    ref_list.append('')
    ref_list.append('   * RuntimeError (Attribute \\`value\\` not set)')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_list.append('')
    ref_text = (os.linesep).join(ref_list)
    if actual_text != ref_text:
        print('STDOUT: {0}'.format(stdout))
        print('STDERR: {0}'.format(stderr))
    assert actual_text == ref_text
    # Test tracing module #2 (simple usage based)
    script_name = os.path.join(script_dir, 'trace_my_module_2.py')
    proc = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    actual_text = remove_header(stdout)
    assert actual_text == ref_text
    # Test cogging
    script_name = os.path.join(script_dir, 'build-docs.sh')
    input_file = os.path.join(script_dir, 'my_module.py')
    output_file = os.path.join(script_dir, 'my_module_out.py')
    with pmisc.ignored(OSError):
        os.remove(output_file)
    bin_dir = os.environ['BIN_DIR']
    proc = subprocess.Popen(
        [
            'python',
            os.path.join(bin_dir, 'cog.py'),
            '-e',
            '-o', output_file,
            input_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()
    retcode = proc.returncode
    if retcode:
        print(stdout)
        raise RuntimeError('Tracing did not complete successfully')
    # Read reference
    ref_fname = os.path.join(script_dir, 'my_module_ref.py')
    with open(ref_fname, 'r') as fobj:
        ref_text = fobj.readlines()
    # Read generated output
    with open(output_file, 'r') as fobj:
        actual_text = fobj.readlines()
    with pmisc.ignored(OSError):
        os.remove(output_file)
    # First line is the file name, which is different
    assert actual_text[1:] == ref_text[1:]


def test_pcontracts_doccode():
    """ Test code used in pcontracts module """
    # pylint: disable=W0612
    from docs.support.pcontracts_example_2 import (custom_contract_a,
                                                  custom_contract_b)
    @pexdoc.pcontracts.contract(name='custom_contract_a')
    def funca(name):
        print('My name is {0}'.format(name))
    @pexdoc.pcontracts.contract(name='custom_contract_b')
    def funcb(name):
        print('My name is {0}'.format(name))
    AE(funca, RuntimeError, 'Only one exception', name='')
    funca('John')
    AE(funcb, RuntimeError, 'Empty', name='')
    AE(funcb, RuntimeError, 'Invalid name', name='[Bracket]')
    funcb('John')
    from docs.support.pcontracts_example_3 import (
        custom_contract1,
        custom_contract2,
        custom_contract3,
        custom_contract4,
        custom_contract5
    )
    from docs.support.pcontracts_example_3 import (
        custom_contract6,
        custom_contract7,
        custom_contract8,
        custom_contract9,
        custom_contract10
    )
    # Contract 1
    @pexdoc.pcontracts.contract(name='custom_contract1')
    def func1(name):
        return name
    AE(func1, RuntimeError, 'Invalid name', name='')
    assert func1('John') == 'John'
    # Contract 2
    @pexdoc.pcontracts.contract(name='custom_contract2')
    def func2(name):
        return name
    AE(func2, RuntimeError, 'Invalid name', name='')
    assert func2('John') == 'John'
    # Contract 3
    @pexdoc.pcontracts.contract(name='custom_contract3')
    def func3(name):
        return name
    AE(func3, ValueError, 'Argument `name` is not valid', name='')
    assert func3('John') == 'John'
    # Contract 4
    @pexdoc.pcontracts.contract(name='custom_contract4')
    def func4(name):
        return name
    AE(func4, ValueError, 'Argument `name` is not valid', name='')
    assert func4('John') == 'John'
    # Contract 5
    @pexdoc.pcontracts.contract(name='custom_contract5')
    def func5(name):
        return name
    AE(func5, RuntimeError, 'Invalid name', name='')
    assert func5('John') == 'John'
    # Contract 6
    @pexdoc.pcontracts.contract(name='custom_contract6')
    def func6(name):
        return name
    AE(func6, RuntimeError, 'Invalid name', name='')
    assert func6('John') == 'John'
    # Contract 7
    @pexdoc.pcontracts.contract(name='custom_contract7')
    def func7(name):
        return name
    AE(func7, OSError, 'File could not be opened', name='')
    assert func7('John') == 'John'
    # Contract 8
    @pexdoc.pcontracts.contract(name='custom_contract8')
    def func8(name):
        return name
    AE(func8, RuntimeError, 'Invalid name', name='')
    assert func8('John') == 'John'
    # Contract 9
    @pexdoc.pcontracts.contract(name='custom_contract9')
    def func9(name):
        return name
    AE(func9, TypeError, 'Argument `name` is not valid', name='')
    assert func9('John') == 'John'
    # Contract 10
    @pexdoc.pcontracts.contract(name='custom_contract10')
    def func10(name):
        return name
    AE(func10, RuntimeError, 'Argument `name` is not valid', name='')
    assert func10('John') == 'John'

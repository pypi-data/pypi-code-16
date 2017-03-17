#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'shmock',
        version = '1.0.0-55',
        description = 'SHell command MOCKer for integration testing',
        long_description = '.. image:: https://travis-ci.org/ImmobilienScout24/shmock.png?branch=master\n   :alt: Travis build status image\n   :align: left\n   :target: https://travis-ci.org/ImmobilienScout24/shmock\n\n.. image:: https://coveralls.io/repos/ImmobilienScout24/shmock/badge.png?branch=master\n    :alt: Coverage status\n    :target: https://coveralls.io/r/ImmobilienScout24/shmock?branch=master\n\n.. image:: https://badge.fury.io/py/shmock.png\n    :alt: Latest PyPI version\n    :target: https://badge.fury.io/py/shmock\n\n\nSHell command MOCK (SHMOCK)\n===========================\n\nPurpose\n-------\n\nTools for system administration typically call lots of programs on the command line. This makes automated testing quite tricky, since you may need to\n\n* run "sudo ....", even though the build system is not allowed to use sudo\n* have tools like "uname" or "ifconfig" produce certain output for testing\n\nshmock helps you by creating mock commands that supersede the system\'s own commands due to a temporarily manipulated $PATH. Based on the command line parameters, mock commands can have different\n\n* output on STDOUT and STDERR\n* exit code\n\nIt is not possible to simulate slowness or commands that behave differently the second time you call them. Command line parsing is very limited, but that\'s not a problem for auto-generated calls. However, these limitations make the implementation very simple.\n\n\nConfiguration\n-------------\n\nTo configure which commands should be mocked (and how), use a dictionary like this:\n\n.. code-block:: python\n\n    commands_to_mock = {\n        \'saynay\': \'Nay sayers say nay.\',\n        \'jonny\': {\n            (): "walker",\n            "foo": "bar",\n            ("b", "goode"): "Go, Jonny, go!",\n            ("be", "bad"): {"stderr": "yup", "returncode": 255},\n            None: {\n                "stdout": "You called me with some unknown parameters.",\n                "stderr": "And I don\'t like that.",\n                "returncode": 1\n            }\n        }\n    }\n\nThe first part uses the most simple way of defining a mocked command: A \'saynay\' command is defined that always prints "Nay sayers say nay." and exits successfully, regardless of command line options.\n\nAfter that, a \'jonny\' command is defined that illustrates the full feature set of the shmock module. The command is defined to\n\n* When called with no parameters, print "walker".\n* When called with a single parameter "foo", print "bar".\n* When called with the two parameters "b" and "goode", print "Go, Jonny, go!".\n* When called with "be bad", print "yup" to standard error and then exit with 255.\n* When called with any other parameters, print "You..." to standard out, print "And..." to standard error and then exit with 1.\n\nUsage\n-----\n\nThe ShellCommandMock is intended to be used in "with" contexts as shown below:\n\n.. code-block:: python\n\n    import os\n    from shmock import ShellCommandMock\n    with ShellCommandMock(commands_to_mock):\n        os.system("echo $PATH")\n\n        os.system("jonny")\n        os.system("jonny b goode")\n        os.system("jonny be bad")\n        os.system("jonny foobar")\n\n    os.system("echo $PATH")\n\nAdvanced Usage\n--------------\n\nSometimes you want to keep the mocked shell commands for further testing/debugging. You can tell shmock to not clean up the mock environment with\n\n.. code-block:: python\n\n    from shmock import ShellCommandMock\n    with ShellCommandMock(commands_to_mock, keep_temp_dir=True):\n        pass\n\nshmock will print the location of the mock environment, so that you can add it to you $PATH.\n\nWhen output is printed, shmock calls print(), and print() automatically appends a newline to the output. As a result, it is currently not possible to produce output that does not end in a newline. This will be fixed once it becomes a problem.\n\nLicense\n-------\n\nCopyright 2015 Immobilien Scout GmbH\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n',
        author = 'Stefan Nordhausen',
        author_email = 'stefan.nordhausen@immobilienscout24.de',
        license = 'Apache License 2.0',
        url = 'https://github.com/ImmobilienScout24/shmock',
        scripts = [],
        packages = ['shmock'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['six'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )

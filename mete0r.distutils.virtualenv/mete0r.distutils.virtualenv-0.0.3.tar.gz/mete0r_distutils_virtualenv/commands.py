# -*- coding: utf-8 -*-
#
#   mete0r.distutils.virtualenv : Manage virtualenvs with requirement files
#   Copyright (C) 2015-2016 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#   License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from distutils.cmd import Command
from subprocess import check_call
import io
import os.path


project_root_directory = '.'


class virtualenv(Command):

    description = 'create a virtualenv environement'

    user_options = [
        (
            'directory=', 'd',
            'Destination directory',
        ), (
            'system-site-packages', None,
            'Give the virtual environment access to the global site-packages.',
        )
    ]

    def initialize_options(self):
        self.directory = project_root_directory
        self.bin_dir = None
        self.system_site_packages = 0

    def finalize_options(self):
        import virtualenv

        if self.directory.startswith('/'):
            self.directory = self.directory
        else:
            self.directory = os.path.abspath(
                os.path.join(
                    project_root_directory,
                    self.directory,
                ),
            )
        home_dir, lib_dir, inc_dir, bin_dir = virtualenv.path_locations(
            self.directory
        )
        self.bin_dir = bin_dir

    def run(self):
        self.create_environment()
        self.pip_install([
            'setuptools',
            'pip',
            'pip-tools>=1.7.0',
        ], upgrade=True)

    def create_environment(self):
        import virtualenv

        kwargs = {
            'site_packages': self.system_site_packages,
        }

        self.announce('virtualenv.create_environment(%r, **%r)' % (
            self.directory,
            kwargs,
        ))
        if self.dry_run:
            return
        virtualenv.create_environment(
            self.directory,
            **kwargs
        )

    def pip_install(self, requirements, upgrade=False):
        pip = os.path.join(self.bin_dir, 'pip')
        cmd = [
            pip, 'install',
        ]
        if upgrade:
            cmd.append('-U')
        cmd.extend(requirements)
        self.execute(
            check_call,
            tuple([cmd]),
        )

    def pip_wheel(self, requirements, output_directory):
        pip = os.path.join(self.bin_dir, 'pip')
        cmd = [
            pip, 'wheel',
        ]
        cmd.extend(requirements)
        cmd.extend([
            '-w', output_directory,
        ])
        self.execute(
            check_call,
            tuple([cmd]),
        )

    def pip_sync(self, requirements, find_links=(), no_index=False):
        pip_sync = os.path.join(self.bin_dir, 'pip-sync')
        cmd = [
            pip_sync,
        ]
        if self.dry_run:
            cmd.extend([
                '--dry-run',
            ])
        for find_link in find_links:
            cmd.extend([
                '-f', find_link
            ])
        if no_index:
            cmd.append('--no-index')
        cmd.append(requirements)
        self.announce('check_call(%r)' % cmd)
        check_call(cmd)

    def pip_compile(self, output_file, requirements, find_links=(),
                    no_index=False, upgrade=False):
        pip_compile = os.path.join(self.bin_dir, 'pip-compile')
        cmd = [
            pip_compile, '-o', output_file,
        ]
        if self.dry_run:
            cmd.extend([
                '--dry-run',
            ])
        for find_link in find_links:
            cmd.extend([
                '-f', find_link
            ])
        if no_index:
            cmd.append('--no-index')
        if upgrade:
            cmd.append('--upgrade')
        cmd.extend(requirements)
        self.announce('check_call(%r)' % cmd)
        check_call(cmd)

    subcommands = [
    ]


class virtualenv_bootstrap_script(Command):

    description = 'generate virtualenv bootstrap script (experimental)'

    bootstrap_script_filename = 'bootstrap-virtualenv.py'
    requirements_filename = 'requirements.txt'

    user_options = [
        (
            'requirement=', 'r',
            'requirements file [default: %s]' % requirements_filename
        ), (
            'output-file=', 'o',
            'output file [default: %s]' % bootstrap_script_filename
        )
    ]

    def initialize_options(self):
        self.output_file = self.bootstrap_script_filename
        self.requirement = self.requirements_filename
        self.virtualenv_support = 'virtualenv_support'

    def finalize_options(self):
        pass

    def run(self):
        import virtualenv
        extra_text = readfile('bootstrap-virtualenv.in')
        script = virtualenv.create_bootstrap_script(
            extra_text,
        )
        with io.open(self.output_file, 'w') as f:
            f.write(script)

        virtualenv_command = self.get_finalized_command('virtualenv')
        virtualenv_command.pip_wheel(
            ['setuptools', 'pip', 'wheel', 'pip-tools>=1.7.0'],
            self.virtualenv_support,
        )
        virtualenv_command.pip_wheel(
            ['-r', self.requirement],
            self.virtualenv_support,
        )


class pip_sync(Command):

    description = \
            'synchronize a virtualenv with the requirements specification.'
    requirements_filename = 'requirements.txt'

    user_options = [
        (
            'requirement=', 'r',
            'requirements file [default: %s]' % requirements_filename
        ), (
            'find-links=', 'f',
            'Look for archives in this directory or on this HTML page'
        ), (
            'no-index', None,
            'Add index URL to generated file',
        )
    ]

    def initialize_options(self):
        self.find_links = None
        self.no_index = 0
        self.requirement = self.requirements_filename

    def finalize_options(self):
        self.ensure_string_list('find_links')
        self.find_links = self.find_links or ()
        self.find_links = filter(lambda x: x, self.find_links)
        self.dump_options()

    def run(self):
        virtualenv_command = self.get_finalized_command('virtualenv')
        virtualenv_command.pip_sync(
            self.requirement,
            find_links=self.find_links,
            no_index=self.no_index,
        )

    subcommands = [
    ]


class pip_compile(Command):

    description = 'compile a requirements file.'

    requirements_filename = 'requirements.txt'
    install_requires_filename = 'requirements.in'

    user_options = [
        (
            'find-links=', 'f',
            'Look for archives in this directory or on this HTML page'
        ), (
            'no-index', None,
            'Add index URL to generated file',
        ), (
            'upgrade', 'U',
            'Try to upgrade all dependencies to their latest versions',
        ), (
            'output-file=', 'o',
            'output file [default: %s]' % (requirements_filename,)
        ), (
            'sources=', 'c',
            'source files [default: %s]' % (install_requires_filename,)
        )
    ]

    def initialize_options(self):
        self.find_links = None
        self.no_index = 0
        self.upgrade = 0
        self.output_file = self.requirements_filename
        self.sources = self.install_requires_filename

    def finalize_options(self):
        self.ensure_string('output_file')
        self.ensure_string_list('find_links')
        self.ensure_string_list('sources')
        self.find_links = self.find_links or ()
        self.find_links = filter(lambda x: x, self.find_links)
        self.dump_options()

    def run(self):
        virtualenv_command = self.get_finalized_command('virtualenv')
        virtualenv_command.pip_compile(
            self.output_file,
            self.sources,
            find_links=self.find_links,
            no_index=self.no_index,
        )


def readfile(filename):
    with io.open(filename, 'r') as f:
        return f.read()

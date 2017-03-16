"""
cib Installs Bears! Your bear management tool.

Usage:
  cib list
  cib show [<bear>]
  cib install [all|<bear>...] [--ignore-deps]
  cib install -c [<coafile>] [--ignore-deps]
  cib uninstall [all|<bear>...]
  cib upgrade [all|<bear>...]
  cib check-deps [all|<bear>...]

Options:
  -h --help      show this screen
  --ignore-deps  do not also install the dependencies
  -c             helps installing all bears from a configuration file

"""
import importlib
import re
import subprocess
import sys

from dependency_management.requirements.DistributionRequirement import (
    DistributionRequirement)
from dependency_management.requirements.PipRequirement import (
    PipRequirement)
from coalib.collecting.Collectors import get_all_bears_names
from coalib.misc.Shell import call_without_output
from coalib.output.ConsoleInteraction import show_bear
from coalib.parsing.ConfParser import ConfParser
from docopt import docopt
from pyprint.ConsolePrinter import ConsolePrinter
from termcolor import colored


def get_output(command):
    r"""
    Runs the command and decodes the output and returns it.

    >>> get_output(['echo', '-n', 'word'])
    'word'

    :param command: The command to be run.
    :return:        The output of the command, decoded.
    """
    function = subprocess.Popen(command, stdout=subprocess.PIPE)
    result, *_ = function.communicate()
    return result.decode("utf-8")


def install_requirements(package_name):
    """
    Imports a package and tries installing its requirements.

    :param package_name:        The package to be imported.
    :param package_failed_list: The list with the packages which their
                                requirements failed installing.
    :return:                    A list with the packages which had their
                                requirements failing to be installed.
    """
    package_failed_list = []
    package_object = importlib.import_module(
        'coala' + package_name + '.' + package_name)
    for requirement in getattr(package_object, package_name).REQUIREMENTS:
        print('  ', end="")
        try:
            if not isinstance(requirement, DistributionRequirement) and (
                                                    requirement.is_installed()):
                print(str(requirement.package) + ' (' + package_name
                      + "'s dependency)" + ' is already installed.  ' + colored(
                      'SKIP!', 'yellow', 'on_grey'))
                continue
        except FileNotFoundError:
            print(str(requirement.manager) + ' is not installed. Cannot'
                  ' install dependencies correctly.  ' + colored(
                  'FAILED!', 'red', 'on_grey'))
            break
        try:
            print(str(requirement.package) + ' (' + package_name
                  + "'s dependency)" + ' is installing...  ', end="")
            if call_without_output(requirement.install_command()):
                print(colored('FAILED!', 'red', 'on_grey'))
                package_failed_list.append(package_name)
            else:
                print(colored('DONE!', 'green', 'on_grey'))
        except OSError:
            package_failed_list.append(package_name)
    return package_failed_list


def check_requirements(package_name):
    """
    Imports a package and tries checking its requirements.

    :param package_name:        The package to be checked.
    """
    try:
        package_object = importlib.import_module(
            'coala' + package_name + '.' + package_name)
    except ImportError:
        print(package_name + ' has missing dependencies.')
        return 1
    for requirement in getattr(package_object, package_name).REQUIREMENTS:
        if requirement.is_installed():
            print(str(requirement.package) + ' is installed.')
        else:
            print(str(requirement.package) + ' is not installed.')


def get_all_bears_names_from_PyPI():
    """
    Gets all the bears names from PyPI, using the link in the description.

    >>> 'PEP8Bear' in get_all_bears_names_from_PyPI()
    True

    :return: A list with all the bear names.
    """
    output = get_output([sys.executable, '-m', 'pip', 'search',
                         "coala.rtfd.org"])
    return re.findall(r"'(\w+)'", output)


def install_bears(bear_names_list, ignore_deps):
    """
    Tries to install each bear from the ``bear_names_list``. Will also check for
    bears which failed to be installed, or their requirements failed to be
    installed.

    :param bear_names_list: The list which contains the names of the bears.
    :param ignore_deps:     An arg which is given to ignore the bears'
                            dependencies.
    """
    bears_failed_list = []
    for bear_name in bear_names_list:
        if PipRequirement(bear_name).is_installed():
            print(bear_name + ' is already installed.  ' + colored(
                  'SKIP!', 'yellow', 'on_grey'))
            if not ignore_deps:
                bears_failed_list += install_requirements(bear_name)
            continue
        print(bear_name + ' is installing...  ', end="")
        if not PipRequirement(bear_name).install_package():
            print(colored('DONE!', 'green', 'on_grey'))
            if not ignore_deps:
                bears_failed_list += install_requirements(bear_name)
        else:
            print(colored('FAILED!', 'red', 'on_grey'))
            bears_failed_list.append(bear_name)

    return bears_failed_list


def show_installed_bears(bear_names_list):
    all_bears_shown = True
    for bear_name in bear_names_list:
        if PipRequirement(bear_name).is_installed():
            package_object = importlib.import_module(
                'coala' + bear_name + '.' + bear_name)
            show_bear(getattr(package_object, bear_name),
                      True, True, ConsolePrinter())
        else:
            all_bears_shown = False

    return all_bears_shown


def main():
    bear_names_list = sorted(
        get_all_bears_names_from_PyPI(), key=lambda s: s.lower())

    args = docopt(__doc__)

    if args['<bear>']:
        temp_args_bears = set([x.lower() for x in args['<bear>']])
        map_bears_dict = dict(zip([x.lower() for x in bear_names_list],
                                  bear_names_list))
        invalid_inputs = []
        valid_inputs = []
        for bear in temp_args_bears:
            if bear in map_bears_dict:
                valid_inputs.append(map_bears_dict[bear])
            else:
                invalid_inputs.append(bear)
        args['<bear>'] = valid_inputs + invalid_inputs
        not_installed_bears = set()

    if args['list']:
        print('This is a list of all the bears you can install:')

        print('\n'.join(bear_names_list))

    elif args['install']:
        if (PipRequirement('coala-bears').is_installed()):
            print('You cannot use cib while the `coala-bears` package is '
                  'installed because cib installed bears will conflict '
                  'with your currently installed ones. Use `pip uninstall '
                  'coala-bears` if you want to use cib.')
            sys.exit(1)
        if args['all']:
            print('Great idea, we are installing all the bears right now.')
            install_bears(bear_names_list, args['--ignore-deps'])
        elif args['-c']:
            if args['<coafile>']:
                file_name = args['<coafile>']
            else:
                file_name = '.coafile'
            gathered_bears_names_set = set()
            sections = ConfParser().parse(file_name)
            for section in sections.values():
                gathered_bears_names_set |= set(section.get('bears'))
            install_bears(gathered_bears_names_set, args['--ignore-deps'])
        else:
            bears_failed_list = install_bears(valid_inputs,
                                              args['--ignore-deps'])

            if invalid_inputs:
                print('\nThe following inputs were not part of the bears list '
                      'and were therefore not installed:\n'
                      + "\n".join(invalid_inputs))

            if bears_failed_list:
                print('Bears that failed installing/their dependencies failed '
                      'installing:\n' + "\n".join(bears_failed_list),
                      file=sys.stderr)

    elif args['upgrade']:
        if args['all']:
            print('Great idea, we are upgrading all the installed '
                  'bears right now.')
            for bear in bear_names_list:
                if PipRequirement(bear).is_installed():
                    print('Upgrading ' + bear + ' now..')
                    PipRequirement(bear).upgrade_package()
        else:
            for bear in valid_inputs:
                print('Upgrading ' + bear + ' now..')
                if (PipRequirement(bear).is_installed() and
                        bear in bear_names_list):
                    PipRequirement(bear).upgrade_package()
                else:
                    not_installed_bears.add(bear)

            if not_installed_bears:
                print('\nThe following bears were not installed and were '
                      'therefore not uninstalled:\n'
                      + "\n".join(not_installed_bears))

            if invalid_inputs:
                print('\nThe following inputs were not bears or were not '
                      'installed and were therefore not upgraded:\n'
                      + "\n".join(invalid_inputs))

    elif args['uninstall']:
        if args['all']:
            print('Bad idea, we are uninstalling all the installed '
                  'bears right now.')
            for bear in bear_names_list:
                if PipRequirement(bear).is_installed():
                    print('Uninstalling ' + bear + ' now..')
                    PipRequirement(bear).uninstall_package()
        else:
            for bear in valid_inputs:
                print('Uninstalling ' + bear + ' now..')
                if (PipRequirement(bear).is_installed() and
                        bear in bear_names_list):
                    PipRequirement(bear).uninstall_package()
                else:
                    not_installed_bears.add(bear)

            if not_installed_bears:
                print('\nThe following bears were not installed and were '
                      'therefore not uninstalled:\n'
                      + "\n".join(not_installed_bears))

            if invalid_inputs:
                print('\nThe following inputs were not bears and were '
                      'therefore not uninstalled:\n'
                      + "\n".join(invalid_inputs))

    elif args['check-deps']:
        if args['all']:
            print('Good idea, we are checking all the installed '
                  'bears right now.')
            for bear in bear_names_list:
                if PipRequirement(bear).is_installed():
                    print('Checking ' + bear + ' now..')
                    check_requirements(bear)
                    print('\n')
        else:
            for bear in valid_inputs:
                print('Checking ' + bear + ' now..')
                if (PipRequirement(bear).is_installed() and
                        bear in bear_names_list):
                    check_requirements(bear)
                    print('\n')
                else:
                    not_installed_bears.add(bear)
                    print('\n')

            if not_installed_bears:
                print('\nThe following bears were not installed and were '
                      'therefore not checked:\n'
                      + "\n".join(not_installed_bears))

            if invalid_inputs:
                print('\nThe following inputs were not bears and were '
                      'therefore not checked:\n'
                      + "\n".join(invalid_inputs))

    elif args['show']:
        if not args['<bear>']:
            show_installed_bears(bear_names_list)

        elif not valid_inputs:
            print('\nThe following bear is invalid and cannot be shown. '
                  'Please see `cib list` to see the full list of bears.\n'
                  + (args['<bear>'][0]))
        else:
            if not show_installed_bears([args['<bear>'][0]]):
                print('\nThe following bear is not installed. Please use `cib '
                      'install ' + (args['<bear>'][0]) + '` to install it.\n')

    else:
        print(__doc__)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())

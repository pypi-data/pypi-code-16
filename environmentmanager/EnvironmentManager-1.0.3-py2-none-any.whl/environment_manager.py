""" Main module that exposes an interface to control the PYTHONPATH environment variable for
    code in development.
"""
__author__ = 'Ian Davis'
__all__ = ['setup', 'EnvironmentConfiguration']

import json
import sys

import config
import os_util


home_directory = os_util.home_directory()
DEFAULT_CONFIGURATION_FILEPATH = os_util.make_path(home_directory, 'dev_environment.cfg')


class EnvironmentConfiguration(config.Configuration):
    """ Provides configuration file support for environment manager.

        INI File format should look as follows:
        [locations]
        workspace_path = C:/path/to/workspace/
        hte_branch = branch-2-second-printer
        windux_branch = trunk

        [directories]
        hte_paths = [
            "ScaleManagement",
            "ScaleManagement/source",
            ...
        ]
        windux_paths = [
            "Windux/Application/shared/sessionHandler/python",
            "Windux/Application/shared/util/licensing",
            "Windux/Application/shared/util/dongleKey",
            ...
        ]
    """
    def __init__(self, file_path):
        default_locations = {
            'workspace_path': os_util.home_directory(),
            'hte_branch': 'trunk',
            'windux_branch': 'trunk',
        }

        default_hte_paths = (
            'ScaleManagement',
            'ScaleManagement/source',
        )

        default_windux_paths = (
            'Windux/Application/shared/sessionHandler/python',
            'Windux/Application/shared/util/licensing',
            'Windux/Application/shared/util/dongleKey',
        )

        default_directory_values = {
            'hte_subdirectories': json.dumps(default_hte_paths, indent=4),
            'windux_subdirectories': json.dumps(default_windux_paths, indent=4)
        }

        self.default_sections = {
            'locations': default_locations,
            'directories': default_directory_values
        }

        super(EnvironmentConfiguration, self).__init__(file_path)

    def _verify_section_integrity(self):
        """ Verify that all sections and their default options exist in the configuration file. """

        needs_rewrite = False

        for section_name, options in self.default_sections.iteritems():
            if section_name not in self.sections:
                self.add_section(name=section_name, options=options)
                needs_rewrite = True
                continue

            section = self.sections[section_name]

            for option_name, option_value in options.iteritems():
                if option_name not in section.options:
                    needs_rewrite = True
                    section.options[option_name] = option_value

        if needs_rewrite:
            self.write()

    def _setup_default_sections(self):
        """ Setup all default sections and their values for a first init. """

        for section_name, options in self.default_sections.iteritems():
            self.add_section(name=section_name, options=options)


def setup(configuration_filepath=DEFAULT_CONFIGURATION_FILEPATH):
    environment_configuration = EnvironmentConfiguration(configuration_filepath)

    workspace_path = environment_configuration['locations']['workspace_path']

    hte_branch = environment_configuration['locations']['hte_branch']
    windux_branch = environment_configuration['locations']['windux_branch']

    hte_branch_path = os_util.make_path(workspace_path, hte_branch)
    windux_branch_path = os_util.make_path(workspace_path, windux_branch)

    hte_subdirectories = json.loads(environment_configuration['directories']['hte_subdirectories'])
    windux_subdirectories = json.loads(environment_configuration['directories']['windux_subdirectories'])

    for hte_subdirectory in hte_subdirectories:
        environment_path = os_util.make_path(hte_branch_path, hte_subdirectory)
        sys.path.append(environment_path)

    for windux_subdirectory in windux_subdirectories:
        environment_path = os_util.make_path(hte_branch_path, hte_subdirectory)
        sys.path.append(environment_path)

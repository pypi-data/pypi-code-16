from .base import Command, subparses
from giles import utils

import chalk
try:
    import ConfigParser as configparser
except ImportError:  # pragma: no cover
    import configparser
import os
import stat
import textwrap


parser = subparses.add_parser(
    'setup',
    help='Configure your Giles workflow manager.'
)
parser.add_argument(
    '-d',
    '--dry-run',
    help='Setup both the .gilesrc and .gilesrc_profile',
    action='store_true'
)
parser.add_argument(
    '-r',
    '--rc',
    help='Setup only the .gilesrc details.',
    action='store_true'
)
parser.add_argument(
    '-p',
    '--profile',
    help='Setup only the.gilesrc_profile details.',
    action='store_true'
)


class Setup(Command):

    name = 'setup'
    parser = parser
    needs_config = False

    def run(self, args):
        welcome_msg = """
        ########################################################
        #
        # Giles configuration
        #
        ########################################################"""

        chalk.green(textwrap.dedent(welcome_msg), opts=('bold',))
        try:
            self._run_configs(args)
        except KeyboardInterrupt:
            raise KeyboardInterrupt('\n\n!!Error: Configuration Incomplete!!')

    def _file_check(self, name):
        exists = os.path.isfile(name)
        if exists:
            chalk.yellow(
                '\nWARNING: "{}" already exists.'.format(name),
                opts=['bold']
            )
            _override = None
            while _override not in ('y', 'n'):
                _input = utils.get_input(
                    'Override "{}" [y/N]: '.format(name)
                )
                _override = _input or 'n'
            if not _override or _override != 'y':
                raise StopIteration()
        return exists

    def _rc_config(self, args, _all=False):
        if _all or args.rc:
            exists = self._file_check(self.giles.rc_name)
            chalk.magenta(
                "\nPlease setup your .gilesrc details",
                opts=('bold',)
            )
            jira_url = utils.get_input(
                'JIRA URL (e.g. https://example.atlassian.net): ',
                required=True
            )
            github_project = utils.get_input(
                'GitHub Project (e.g. anthonyalmarza/giles): ',
                required=True
            )
            github_repo = utils.get_input('Git Repo Path (default: "."): ')
            github_branch = utils.get_input(
                'Git Default Branch (master): '
            )
            if not args.dry_run:
                config = configparser.RawConfigParser()
                config.add_section('jira')
                config.add_section('github')
                config.set('jira', 'url', jira_url)
                config.set('github', 'project', github_project)
                config.set('github', 'repo_path', github_repo or '.')
                config.set('github', 'branch', github_branch or 'master')
                # Writing our configuration file to 'example.cfg'
                with open(self.giles.rc_name, 'wb') as configfile:
                    config.write(configfile)
            else:
                chalk.blue('DryRun:', opts=['bold'])

            chalk.blue(
                '"{}" setup complete'.format(self.giles.rc_name),
                opts=['bold']
            )

    def _profile_config(self, args, _all=False):
        if _all or args.profile:
            exists = self._file_check(self.giles.profile_name)
            chalk.magenta(
                "\nPlease setup your .gilesrc_profile details",
                opts=('bold',)
            )
            jira_username = utils.get_input(
                'JIRA Username: ',
                required=True
            )
            jira_password = utils.get_input(
                'JIRA Password: ',
                required=True,
                secret=True
            )

            github_username = utils.get_input(
                'GitHub Username: ',
                required=True
            )
            github_password = utils.get_input(
                'GitHub Password: ',
                required=True,
                secret=True
            )
            if not args.dry_run:
                profile = configparser.RawConfigParser()
                profile.add_section('jira')
                profile.add_section('github')
                profile.set('jira', 'username', jira_username)
                profile.set('jira', 'password', jira_password)
                profile.set('github', 'username', github_username)
                profile.set('github', 'password', github_password)
                if exists:
                    os.remove(self.giles.profile_name)
                with open(self.giles.profile_name, 'wb') as configfile:
                    profile.write(configfile)
                    os.chmod(self.giles.profile_name, stat.S_IREAD)
            else:
                chalk.blue('DryRun:', opts=['bold'])
            chalk.blue(
                '"{}" setup complete'.format(self.giles.profile_name),
                opts=['bold']
            )

    def _run_configs(self, args):
        _all = not args.rc and not args.profile
        for config in (self._rc_config, self._profile_config):
            try:
                config(args, _all=_all)
            except StopIteration:
                pass
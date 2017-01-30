""" standard """
import argparse
import inflect
import json
import os
import re
import shutil
import six
import subprocess
import sys
import zipfile
# from builtins import bytes
from setuptools.command import easy_install

""" third-party """
try:
    from jsonschema import SchemaError, ValidationError, validate
except ImportError as e:
    print('Error: {}'.format(e))
    print('Try app.py --lib or adding jsonschema to setup.py')

# Load Schema
schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tcex_json_schema.json')
with open(schema_file) as fh:
    schema = json.load(fh)


class TcExLocal:
    """
    Class to support running local instance TcEx Apps
    """

    def __init__(self):
        """
        """
        # init inflect engine
        self.inflect = inflect.engine()

        # Required Argument
        # self._parsed = False  # only parse once from user
        self._config = {}
        self._parser = argparse.ArgumentParser()

        self._install_json = {}
        # self.load_install_json()
        self._app_packages = []

        self._required_arguments()
        self._args, self._extra_args = self._parser.parse_known_args()

    def _load_config(self):
        """Load the configuration file."""
        if not os.path.isfile(self._args.config):
            msg = 'Provided config file does not exist ({0}).'
            msg.format(self._args.config)
            self._exit(msg, 1)

        with open(self._args.config) as data_file:
            self._config = json.load(data_file)

    def _parameters(self, args):
        """Build CLI arguments to pass to script on the command line.

        This method takes the json data and covert it to CLI args for the execution
        of the script.

        Returns:
            (str): A string containing all parameter to pass to script
        """
        parameters = ' '
        for config_key, config_val in args.items():
            if isinstance(config_val, bool):
                if config_val:
                    parameters += '--{0} '.format(config_key)
            elif isinstance(config_val, list):
                for val in config_val:
                    parameters += '--{0} {1} '.format(
                        config_key, self._wrap(val))
            elif isinstance(config_val, dict):
                msg = 'Error: Dictionary types are not currently supported for field {}'
                msg.format(config_val)
                self._exit(msg, 1)
            else:
                """
                Special use case just for Jenkins builds to overwrite values in tc-jenkins.json
                This can't be used for arguments names already used by app.py
                """
                try:
                    self._parser.add_argument('--{}'.format(config_key), required=False)
                    self._args, self._new_extra_args = self._parser.parse_known_args()
                except argparse.ArgumentError:
                    pass

                args_config_value = getattr(self._args, config_key)
                if args_config_value is not None:
                    parameters += '--{0} {1} '.format(
                        config_key, self._wrap(str(args_config_value)))
                else:
                    parameters += '--{0} {1} '.format(
                        config_key, self._wrap(str(config_val)))

        return parameters

    def _required_arguments(self):
        """Required arguments for this class to function"""

        # actions
        self._parser.add_argument(
            '--lib', action='store_true', help='Gen the libs')
        self._parser.add_argument(
            '--package', action='store_true', help='Package the app')
        self._parser.add_argument(
            '--run', action='store_true', help='Run the app')
        self._parser.add_argument(
            '--validate', action='store_true', help='Validate JSON configs')

        # run args
        self._parser.add_argument(
            '--config', default='tc.json', help='The configuration file')
        self._parser.add_argument(
            '--script', default=None, help='The Python script name')
        self._parser.add_argument(
            '--group', default=None, help='The group of profiles to executed')
        self._parser.add_argument(
            '--python', default='python', help='The python executable')
        self._parser.add_argument(
            '--profile', default='default', help='The profile to be executed')
        self._parser.add_argument(
            '--quiet', action='store_true', help='Suppress output')

        # validate args
        self._parser.add_argument(
            '--install_json', default='install.json', help='The install.json filename')

        # package args
        self._parser.add_argument(
            '--collection', action='store_true', help='Build app collection')
        self._parser.add_argument(
            '--zip_out', default=None, help='The zip output path')

    @property
    def args(self):
        """The parsed args

        Returns:
            (namespace): ArgParser parsed arguments
        """
        return self._args

    @property
    def parser(self):
        """The ArgParser parser object

        Returns:
            (ArgumentParser): TcEx local parser object
        """
        return self._parser

    @property
    def run(self):
        """Execute the script with arguments provided in tc.json."""

        # load tc config
        self._load_config()

        # TODO: Output profile name
        selected_profiles = {}
        for profile, config in self._config.get('profiles').items():
            if profile == self._args.profile:
                selected_profiles[profile] = config
            elif config.get('group') is not None and config.get('group') == self._args.group:
                selected_profiles[profile] = config

        command_count = 0
        status_code = 0
        for profile, sp in selected_profiles.items():
            print('Profile: {}'.format(profile))
            command_count += 1

            # get script name
            script = sp.get('script')
            if self._args.script is not None:
                script = self._args.script

            if script is None:
                self._exit('No script provided', 1)

            command = '{0} . {1} {2}'.format(
                self._args.python,
                script.replace('.py', ''),  # TODO: replace with regex to end of line
                self._parameters(sp.get('args')))
            print('Executing: {}'.format(command))

            p = subprocess.Popen(
                command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print('Exit Code: {}'.format(p.returncode))

            if not sp.get('quiet') and not self._args.quiet:
                print(self.to_string(out, 'ignore'))
                if len(err) != 0:
                    print('Error: {}'.format(err))
            if p.returncode != 0:
                status_code = p.returncode
                break

        msg = 'Executed {}'.format(self.inflect.no('command', command_count))
        self._exit(msg, status_code)

    def load_install_json(self):
        """Read the install.json file"""
        with open('install.json') as fh:
            self._install_json = json.load(fh)

    def package(self):
        """Package the app for deployment

        This method will package the app for deployment to ThreatConnect.  It will download
        all required dependencies and include them in the package.  Validating of the
        install.json file or files will be automatically run before packaging the app.
        """

        lib_directory = 'lib_{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        app_path = os.getcwd()
        contents = os.listdir(app_path)

        # create build directory
        tmp_path = os.path.join(os.sep, 'tmp', 'tcex_builds')
        if not os.path.isdir(tmp_path):
            os.mkdir(tmp_path)

        # copy project directory to temp location to use as template for multiple builds
        base_name = os.path.basename(app_path)
        template_app_path = os.path.join(tmp_path, base_name)
        if os.access(template_app_path, os.W_OK):
            # cleanup any previous failed builds
            shutil.rmtree(template_app_path)

        # ignore unwanted files from build to ensure app packages are minimum size
        ignore_patterns = shutil.ignore_patterns(
            '*.git*', 'lib', '*log', '*python-version', 'tc.json', '*.tcx')
        shutil.copytree(app_path, template_app_path, False, ignore_patterns)

        for install_json in contents:
            if 'install.json' not in install_json:
                continue

            self.validate(install_json)

            base_name = os.path.basename(app_path)
            if install_json == 'install.json':
                app_name = base_name
            else:
                app_name = install_json.split('.')[0]

            tmp_app_path = os.path.join(tmp_path, app_name)
            if tmp_app_path != template_app_path:
                shutil.copytree(template_app_path, tmp_app_path)

            lib_path = os.path.join(tmp_app_path, lib_directory)
            if os.access(lib_path, os.W_OK):
                shutil.rmtree(lib_path)
            os.mkdir(lib_path)

            os.environ['PYTHONPATH'] = '{0}'.format(lib_path)
            stdout = sys.stdout
            stderr = sys.stderr
            try:
                with open(os.path.join(app_path, '{}-package.log'.format(app_name)), 'w') as log:
                    sys.stdout = log
                    sys.stderr = log
                    easy_install.main(['-axZ', '-d', lib_path, str(tmp_app_path)])
            except SystemExit as e:
                raise Exception(str(e))
            finally:
                sys.stdout = stdout
                sys.stderr = stderr

            if len(os.listdir(lib_path)) == 0:
                raise Exception('Encountered error running easy_install for {}.  Check log file for details.'.format(
                    app_name))

            # cleanup
            git_path = os.path.join(tmp_app_path, '.git')
            if os.access(git_path, os.W_OK):
                shutil.rmtree(git_path)
            build_path = os.path.join(tmp_app_path, 'build')
            if os.access(build_path, os.W_OK):
                shutil.rmtree(build_path)

            # rename install.json
            if install_json != 'install.json':
                install_json_path = os.path.join(tmp_app_path, install_json)
                if os.access(build_path, os.W_OK):
                    shutil.rmtree(install_json_path)
                shutil.move(install_json_path, os.path.join(tmp_app_path, 'install.json'))

            # zip build directory
            zip_file = os.path.join(app_path, app_name)
            if self._args.zip_out is not None and os.access(self._args.zip_out, os.W_OK):
                zip_file = os.path.join(self._args.zip_out, app_name)

            zip_file_zip = '{}.zip'.format(zip_file)
            zip_file_tcx = '{}.tcx'.format(zip_file)
            shutil.make_archive(zip_file, 'zip', tmp_path, app_name)
            shutil.move(zip_file_zip, zip_file_tcx)
            self._app_packages.append(zip_file_tcx)

            # cleanup build directory
            if install_json != 'install.json':
                shutil.rmtree(tmp_app_path)

        if self._args.collection and len(self._app_packages) > 0:
            collection_file = '{}.zip'.format(base_name)
            z = zipfile.ZipFile(collection_file, 'w')
            for app in self._app_packages:
                z.write(app, os.path.basename(app))
            z.close
            if self._args.zip_out is not None and os.access(self._args.zip_out, os.W_OK):
                collection_zip = os.path.join(self._args.zip_out, collection_file)
                shutil.move(collection_file, collection_zip)

        # cleanup template directory
        if os.access(template_app_path, os.W_OK):
            shutil.rmtree(template_app_path)

    @staticmethod
    def _exit(message, code=0):
        """Exit the script

        Args:
            message (str): An exit message
            code (Optional [int]): The exit status code
        """
        print('{} (exit code: {})'.format(message, code))
        sys.exit(code)

    @staticmethod
    def gen_lib():
        """Build libs locally for app

        Using the setup.py this method will install all required python modules locally
        to be used for local testing.
        """
        lib_directory = 'lib_{}.{}.{}'.format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        app_path = os.getcwd()
        app_name = os.path.basename(app_path)

        lib_path = os.path.join(app_path, lib_directory)
        if not os.path.isdir(lib_path):
            os.mkdir(lib_path)

        os.environ['PYTHONPATH'] = '{0}'.format(lib_path)
        stdout = sys.stdout
        stderr = sys.stderr
        try:
            with open(os.path.join(app_path, '{}-libs.log'.format(app_name)), 'w') as log:
                sys.stdout = log
                sys.stderr = log
                easy_install.main(['-axZ', '-d', lib_path, str(app_path)])
        except SystemExit as e:
            raise Exception(str(e))
        finally:
            sys.stdout = stdout
            sys.stderr = stderr

        if len(os.listdir(lib_path)) == 0:
            raise Exception('Encountered error running easy_install for {}.  Check log file for details.'.format(
                app_name))

        build_path = os.path.join(app_path, 'build')
        if os.access(build_path, os.W_OK):
            shutil.rmtree(build_path)
        temp_path = os.path.join(app_path, 'temp')
        if os.access(temp_path, os.W_OK):
            shutil.rmtree(temp_path)

    @staticmethod
    def to_string(data, errors='strict'):
        """Covert x to string in Python 2/3

        Args:
            data (any): Data to ve validated and re-encoded

        Returns:
            (any): Return validate or encoded data

        """
        # TODO: Find better way using six or unicode_literals
        if isinstance(data, (bytes, str)):
            try:
                data = unicode(data, 'utf-8', errors=errors)  # 2to3 converts unicode to str
            except NameError:
                data = str(data, 'utf-8', errors=errors)
        return data

    @staticmethod
    def validate(install_json):
        """Validate install.json file for required parameters"""

        # install.json validation
        try:
            with open(install_json) as fh:
                data = json.loads(fh.read())
            validate(data, schema)
            print('{} is valid'.format(install_json))
        except SchemaError as e:
            print('{} is invalid "{}"'.format(install_json, e))
        except ValidationError as e:
            print('{} is invalid "{}"'.format(install_json, e))

    @staticmethod
    def _wrap(data):
        """Wrap any parameters that contain spaces

        Returns:
            (string): String containing parameters wrapped in double quotes
        """
        if len(re.findall(r'[!\-\s\$]{1,}', data)) > 0:
            data = '\'{}\''.format(data)
        return data
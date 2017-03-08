import os
import json
from click import ClickException
from vsscli import __version__
from pyvss import manager
from pyvss import __version__ as __pyvss_version__
from pyvss.manager import VssManager, VssError
from base64 import b64decode, b64encode


class VssCLIError(ClickException):
    pass


class CLIManager(VssManager):
    user_agent = 'vsscli/{}+pyvss/{}'.format(__version__,
                                             __pyvss_version__)

    def __init__(self, click, config, tk=None,
                 verbose=False,
                 username=None, password=None,
                 output=None):
        super(CLIManager, self).__init__(tk)
        self.click = click
        self.output = output
        # config dir/file
        self.full_config_path = os.path.expanduser(config)
        # endpoints
        self.base_endpoint = manager.API_ENDPOINT_BASE
        self.api_endpoint = manager.API_ENDPOINT
        self.token_endpoint = manager.TOKEN_ENDPOINT
        # sets verbose level
        self.verbose = verbose
        # sets username if any
        self.username = username
        # sets password if any
        self.password = password

    @property
    def output_json(self):
        return self.output == 'json'

    def configure(self, username, password):
        self.username = username
        self.password = password
        # directory available
        if os.path.isdir(os.path.dirname(self.full_config_path)):
            pass
        else:
            os.mkdir(os.path.dirname(self.full_config_path))
        # config file
        if os.path.isfile(self.full_config_path):
            try:
                e_username, e_password, e_api_token = \
                    self.load_config_file()
                if e_username and e_password and e_api_token:
                    confirm = self.click.confirm(
                        'Would you like to replace existing configuration?')
                    if confirm:
                        self.write_config_file()
                else:
                    self.click.echo(
                        'Successfully configured. '
                        'You are ready to use VSS CLI.')
            except VssCLIError, ex:
                self.click.echo(ex)
                confirm = self.click.confirm(
                    'Would you like to replace existing configuration?')
                if confirm:
                    self.write_config_file()
        else:
            self.write_config_file()

    def load_config_file(self):
        try:
            with open(self.full_config_path, 'r') as f:
                profiles = json.load(f)
                profile = profiles[self.base_endpoint]
                credentials_decoded = b64decode(profile['auth'])
                token = profile['token']
                username, password = credentials_decoded.split(':')
            return username, password, token
        except ValueError, ex:
            raise VssCLIError('Invalid configuration file.')

    def load_config(self):
        try:
            # check for environment variables
            if os.environ.get('VSS_API_TOKEN') or \
                    (os.environ.get('VSS_API_USER') and
                     os.environ.get('VSS_API_USER_PASS')):
                # don't load config file
                if os.environ.get('VSS_API_TOKEN'):
                    # set api token
                    self.api_token = os.environ.get('VSS_API_TOKEN')
                    return self.username, self.password, self.api_token
                elif os.environ.get('VSS_API_USER') \
                        and os.environ.get('VSS_API_USER_PASS'):
                    # generate a new token - won't save
                    try:
                        self.get_token()
                    except VssError, ex:
                        raise VssCLIError(ex.message)
                    return self.username, self.password, self.api_token
                else:
                    raise VssCLIError(
                        'Environment variables error. Please, verify '
                        'VSS_API_TOKEN or VSS_API_USER and VSS_API_USER_PASS')
            else:
                if os.path.isfile(self.full_config_path):
                    # read config and look for profile
                    self.username, self.password, self.api_token = \
                        self.load_config_file()
                    try:
                        self.whoami()
                    except VssError, ex:
                        if self.verbose:
                            self.click.echo(ex)
                        self.api_token = self.get_token(self.username,
                                                        self.password)
                        self.write_config_file(new_token=self.api_token)
                    return self.username, self.password, self.api_token
            raise VssCLIError("Invalid configuration. "
                              "Please, run "
                              "'vss configure' to initialize config")
        except Exception, ex:
            raise VssCLIError(str(ex.message))

    def write_config_file(self, new_token=None):
        credentials = '{}:{}'.format(self.username, self.password)
        token = new_token or self.get_token(self.username,
                                            self.password)
        with open(self.full_config_path, 'wb') as fp:
            config_dict = {self.base_endpoint: {
                'auth': b64encode(credentials),
                'token': token}
            }
            json.dump(config_dict, fp,
                      sort_keys=True,
                      indent=4)
            self.click.echo('Successfully written configuration '
                            'file {}'.format(self.full_config_path))

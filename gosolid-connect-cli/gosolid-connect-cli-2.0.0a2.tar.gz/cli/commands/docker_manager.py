import requests
import json
import os
import cli.configuration
import cli.messages
import boto3
import docker
import subprocess
import sys
from cli.framework.git_core import Git

# TODO: REFACTOR parse_task_definitions AND check_ecr_login TO ECR CLASS


class Docker(object):
    def __init__(self, prop, user_data, directory):
        self.directory = directory
        self.environment_code = None
        if prop is None:
            self.cwd = os.getcwd()
            self.connect_file = os.path.join(self.cwd + '/.connect')
            self.property = self.get_property_from_dir()[0].strip()
            self.environment_code = self.get_property_from_dir()[1].strip()
        else:
            self.property = prop
            if self.directory is not None:
                self.cwd = os.path.join(os.getcwd() + '/%s' % self.directory)
            else:
                self.cwd = os.path.join(os.getcwd() + '/%s' % self.property)
            self.connect_file = os.path.join(self.cwd + '/.connect')

        self.docker_interface = docker.from_env(timeout=60)

        self.property_url = cli.configuration.BASE_URL + 'property/%s' % self.property
        self.environment_list = self.property_url + "/environments"
        self.git_folder = os.path.join(self.cwd + '/.git')

        self.user_data = user_data
        self.environments = None
        self.environment_data = None
        self.property_data = None
        self.task_definition = None
        self.parsed_task_definitions = None
        self.aws_token = None
        self.aws_endpoint = None

        self.no_env_error = cli.messages.ERR_NO_ENVIRONMENT % self.property
        self.refresh_property_data()
        self.refresh_environment_data()

    def refresh_property_data(self):
        """Get the latest property data from Connect"""
        data = requests.get(self.property_url, headers={
            'email': self.user_data['email'],
            'secret-key': self.user_data['secret_key']
        })
        reply = json.loads(data.text)
        if reply['success']:
            self.property_data = reply['result']
            return True
        else:
            print(reply['errors'][0]['messages'][0])
            return False

    def get_property_from_dir(self):
        """
        If no property code was provided (as would be the case with a "connect start"), check the working dir for
        .connect file, which contains the property and environment codes
        """
        if os.path.exists(self.connect_file):
            with open(self.connect_file, 'r') as f:
                lines = f.readlines()
                if lines[0] == '':
                    return None
                else:
                    return [lines[0], lines[1]]
        else:
            print('FATAL: No property name set. For help, run "connect -h".')
            sys.exit()

    def refresh_environment_data(self):
        """Get the latest environment data from Connect"""
        data = requests.get(self.environment_list, headers={
            'email': self.user_data['email'],
            'secret-key': self.user_data['secret_key']
        })
        reply = json.loads(data.text)
        if reply['success']:
            self.environments = reply['result']
        else:
            print(reply['errors'][0]['messages'][0])

    def get_environment(self):
        """
        Get data about a given environment
        Run the task definitions through a parser to be fed to docker-py
        """
        if self.environment_code is None:
            print('\nWhich environment would you like to start?')
            for env in self.environments:
                print('%s (%s)' % (env['code'], env['label']))
            self.environment_code = raw_input("Environment code: ")
        codes = [env['code'] for env in self.environments]
        if self.environment_code in codes:
            environment_url = cli.configuration.BASE_URL + 'environment/%s' % self.environment_code
            data = requests.get(environment_url, headers={
                'email': self.user_data['email'],
                'secret-key': self.user_data['secret_key']
            })
            reply = json.loads(data.text)
            if reply['success']:
                self.environment_data = reply['result']
                self.environment_code = self.environment_data['code']
                self.task_definition = json.loads(self.environment_data['task_definition'])
                self.parse_task_definition()
            else:
                print(reply['errors'][0]['messages'][0])
        else:
            print(cli.messages.ERR_INVALID_ENVIRONMENT)
            self.get_environment()

    def parse_task_definition(self):
        """
        Take JSON-encoded list of task definitions from EC2, and parse them into dictionaries
        by section, to be fed in to docker-py
        """
        task_definitions = {
            'ports': {},
            'volumes': {},
            'environment': {}
        }
        container_definitions = self.task_definition['containerDefinitions'][0]

        # Map all ports
        for mapping in container_definitions['portMappings']:
            task_definitions['ports'][str(mapping['containerPort'])+'/tcp'] = mapping['hostPort']

        # Mount volumes on the host system
        for mount in container_definitions['mountPoints']:
            source = mount['sourceVolume'].replace('`pwd`', os.getcwd())
            destination = mount['containerPath'].replace('`pwd`', os.getcwd())
            task_definitions['volumes'][source] = {
                'bind': destination,
                'mode': 'ro' if mount['readOnly'] else 'rw'
            }

        # Send environment variables
        for mount in container_definitions['environment']:
            task_definitions['environment'][mount['name']] = mount['value']

        self.parsed_task_definitions = task_definitions

    def check_ecr_login(self):
        """
        Get Docker credentials from ECR to push/pull Docker images
        Performs error handling for if AWS CLI has not been set up yet
        """
        try:
            client = boto3.client('ecr', region_name="us-west-2")
            response = client.get_authorization_token(registryIds=[cli.configuration.AWS_ACCOUNT_ID, ])
            self.aws_token = response["authorizationData"][0]["authorizationToken"]
            self.aws_endpoint = response["authorizationData"][0]["proxyEndpoint"]
        except Exception as e:
            print('ERROR:', str(e))
            print(cli.messages.AWS_INCORRECT_CONFIGURATION)
            exit(0)

    def init(self):
        """
        Check out code to specified directory
        Write property and environment codes to .connect file (to avoid excessive API calls)
        Start development environment
        """
        if self.environment_data is None:
            self.get_environment()
        if not os.path.exists(self.connect_file):
            name = self.property_data['name']
            print('Creating development environment for %s...' % name)
            if not os.path.exists(self.git_folder):
                Git(self.property_data, self.user_data, self.directory).init_repo()
            # w+ file mode overwrites everything already present in the file
            with open(self.connect_file, 'w+') as f:
                f.seek(0)
                f.write(self.property_data['code'].lower()+'\n')
                f.write(self.environment_data['code'])
                f.flush()
            print(cli.messages.SUCCESS_INIT % name)
            self.start()
        else:
            print(cli.messages.ERR_INIT_ERROR_EXISTS)
            sys.exit()

    def start(self):
        """
        Gets task definitions if they don't exist
        Ensures that AWS token is present and ECR login is valid
        Creates docker environment
        """
        os.chdir(self.cwd)
        if self.task_definition is None:
            self.get_environment()
        if self.aws_token is None:
            self.check_ecr_login()
        try:
            self.docker_interface.login(username="AWS", password=self.aws_token, registry=self.aws_endpoint)
            container_name = '%s:%s' % (cli.configuration.AWS_ECR_BASE, self.property.lower())
            name = '%s.%s' % (self.property.lower(), self.environment_code)
            self.docker_interface.containers.run(container_name,
                                                 name=name,
                                                 ports=self.parsed_task_definitions['ports'],
                                                 volumes=self.parsed_task_definitions['volumes'],
                                                 environment=self.parsed_task_definitions['environment'],
                                                 detach=True)
            # TODO: Get this to output without locking up on wait command
            # log_stream = docker.APIClient(base_url='unix://var/run/docker.sock').attach(name, stream=True)
            # for line in log_stream:
            #     print(line.decode("utf-8").rstrip('\n'))

            print(cli.messages.SUCCESS_START % 'localhost')
        except docker.errors.APIError:
            self.execute('start')
            print(cli.messages.SUCCESS_START % 'localhost')
        except Exception as e:
            print('ERROR:', str(e))
            print(cli.messages.ERR_DOCKER_LAUNCH)
            exit(0)

    def execute(self, method):
        """
        Used for executing generic commands with which there is an exact match in docker-py
        """
        if self.environment_code is None:
            self.get_environment()
        os.chdir(self.cwd)
        container = self.docker_interface.containers.get('%s.%s' % (self.property.lower(),
                                                                    self.environment_code))
        getattr(container, method)()

    def stop(self):
        try:
            self.execute('stop')
            print(cli.messages.SUCCESS_STOP)
        except docker.errors.NotFound:
            print(cli.messages.ERR_NO_ENVIRONMENT % '<property_code>')

    def remove(self):
        try:
            self.execute('remove')
            print(cli.messages.SUCCESS_STOP)
        except docker.errors.APIError:
            print(cli.messages.ERR_MUST_STOP_BOX)
        except docker.errors.NotFound:
            print(cli.messages.ERR_NO_ENVIRONMENT % '<property_code>')

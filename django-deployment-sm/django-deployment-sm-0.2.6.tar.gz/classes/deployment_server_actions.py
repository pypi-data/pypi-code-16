import os

from fabric.api import *
from fabric.tasks import execute
from fabric.contrib.files import exists
from fabric.operations import put

from .exceptions import DeploymentException


class DeploymentServerActions(object):
    """
    The DeploymentServerActions class is a helper class for running shell commands on the server

    """

    DEPLOYED = 'deployed'
    PYTHON_2 = 'python'
    PYTHON_3 = 'python3'

    def __init__(self, config_item):
        """
        :param config_item:
        :type config_item: ConfigItem
        """
        self.config_item = config_item
        self.create_directory(self.config_item.deploy_dir)

    @property
    def deployed_path(self):
        """
        Concatination of deploy dir and deployed

        :return:
        """
        return os.path.join(self.config_item.deploy_dir, self.DEPLOYED)

    @property
    def virtualenv_path(self):
        """
        Concatination of virtualenv

        :return:
        """
        return os.path.join(self.config_item.deploy_dir, 'virtualenv')

    @property
    def python_path(self):
        """
        Concatination of virtualenv and python

        :return:
        """
        return os.path.join(os.path.join(self.virtualenv_path, 'bin'), 'python')

    @property
    def pip_path(self):
        """
        Concatination of virtulanev and pip

        :return:
        """
        return os.path.join(os.path.join(self.virtualenv_path, 'bin'), 'pip')

    def manage_py_full_path(self, to_deploy_commit_hash):
        """
        Full path of the manage.py in the newly deployed directory

        :param to_deploy_commit_hash:
        :return:
        """
        return os.path.join(
            os.path.join(
                self.config_item.deploy_dir,
                to_deploy_commit_hash
            ),
            self.config_item.manage_py.path
        )

    def _get_current_revision(self):
        """
        Gets the current deployed revision on the server

        :return:
        """
        if exists(self.deployed_path):
            return sudo('readlink {}'.format(self.deployed_path))
        else:
            return None

    def _execute_service_command(self, service, service_command):
        """
        Execute a command on a service through the service_management_command

        :param service: celery, gunicorn, wsgi...
        :param service_command: stop, start, reload, bla
        :return:
        """
        service_management_command = self.config_item.service_management_command

        if service_management_command == 'service':
            execute_string = '{service_management_command} {service} {command}'
        elif service_management_command == 'systemctl':
            execute_string = '{service_management_command} {command} {service}'
        else:
            raise DeploymentException(
                'Do you have a custom service running on your system? Please contact the django-deploy team.'
            )

        return sudo(
            execute_string.format(
                service_management_command=service_management_command,
                service=service,
                command=service_command,
            ),
            warn_only=True,
        )

    def _command_services_wrapper(self, command):
        """
        Executes the services in the config file

        :param command:
        :return:
        """
        for service in self.config_item.get_services_list():
            service_config_object = getattr(self.config_item.services, service)
            if command in service_config_object.__dict__:
                self.execute_with_host(
                    self._execute_service_command,
                    service=service,
                    service_command=getattr(service_config_object, command),
                )

    def _execute_manage_py_command(self, to_deploy_commit_hash, manage_py_command):
        """
        Executes the manage.py with the virtualenv and a specific command

        :param to_deploy_commit_hash:
        :param manage_py_command: migrate, collectstatic
        :return:
        """
        with cd(os.path.join(self.config_item.deploy_dir, to_deploy_commit_hash)):
            return sudo(
                '{python_virtualenv} {manage_py_full_path} {manage_py_command}'.format(
                    python_virtualenv='virtualenv/bin/python',
                    manage_py_full_path=self.config_item.manage_py.path,
                    manage_py_command=manage_py_command,
                )
            )

    def _set_symbolic_link(self, source_path, destination_path):
        """
        Set a symbolic link from source path to destination path
        ** Existing links will be deleted **

        :param source_path:
        :param destination_path:
        :return:
        """
        # Remove link if there is any
        self._remove_file_or_dir(destination_path)
        return sudo(
            'ln -sf {source_path} {destination_path}'.format(
                source_path=source_path,
                destination_path=destination_path,
            ),
            warn_only=True
        )

    def set_symbolic_link(self, source_path, destination_path):
        """
        See _set_symbolic_link

        :param source_path:
        :param destination_path:
        :return:
        """
        return self.execute_with_host(
            self._set_symbolic_link,
            source_path=source_path,
            destination_path=destination_path,
        )

    def execute_all_manage_py_commands(self, to_deploy_commit_hash):
        """
        Executes all manage.py commands in the config in the order of the list

        :param to_deploy_commit_hash:
        :return:
        """
        for manage_py_command in self.config_item.manage_py.actions:
            self.execute_with_host(
                self._execute_manage_py_command,
                to_deploy_commit_hash=to_deploy_commit_hash,
                manage_py_command=manage_py_command,
            )

    def stop_services(self):
        """
        Stops all services

        :return:
        """
        self._command_services_wrapper('stop')

    def start_services(self):
        """
        Starts all services

        :return:
        """
        self._command_services_wrapper('start')

    def has_virtualenv(self):
        """
        If the host has a virtualenv

        :return:
        """
        return self.execute_with_host(self._has_virtualenv).get(self.config_item.host)

    def update_virtualenv(self, to_deploy_commit_hash):
        """
        Updates virtualenv with the given requirements.txt in the config

        :param to_deploy_commit_hash:
        :return:
        """
        return self.execute_with_host(self._update_virtualenv, to_deploy_commit_hash=to_deploy_commit_hash)

    def _update_virtualenv(self, to_deploy_commit_hash):
        return sudo('{pip} install -r {requirements_txt}'.format(
            pip=self.pip_path,
            requirements_txt=os.path.join(
                os.path.join(
                    self.config_item.deploy_dir,
                    to_deploy_commit_hash
                ),
                self.config_item.requirements_txt
            )
        ))

    def _run_command(self, command):
        return sudo(command)

    def run_command(self, command):
        return self.execute_with_host(self._run_command, command=command)

    def create_virtualenv(self):
        return self.execute_with_host(self._create_virtualenv)

    def _create_virtualenv(self):
        """
        Creates the virtualenv in der deployment dir

        :return:
        """
        if self.config_item.python_version == self.PYTHON_2:
            return sudo('virtualenv {}'.format(self.virtualenv_path))
        elif self.config_item.python_version == self.PYTHON_3:
            return sudo('python3 -m venv {}'.format(self.virtualenv_path))

    def _has_virtualenv(self):
        """
        Looks for the virtualenv

        :return:
        """
        return exists(self.virtualenv_path, use_sudo=True)

    def _create_directory(self, directory):
        """
        Create the directory tree without overwriting the current tree (-p)

        :return:
        """
        sudo('mkdir -p {}'.format(directory))

    def _push_file_to_server(self, source_path, server_path):
        """
        Pushes the source file to server_path

        :return:
        """
        return put(source_path, server_path, use_sudo=True)

    def _unpack_tar_to_source(self, tar_path, unpack_to):
        """
        Unpacks a tar.gz to a source on the host

        :return:
        """
        return sudo('tar xf {tar_path} -C {unpack_to}'.format(tar_path=tar_path, unpack_to=unpack_to))

    def _remove_file_or_dir(self, source):
        """
        Removes a file or a directory on the server

        :param source:
        :return:
        """
        return sudo('rm -rf {}'.format(source))

    def remove_file_or_dir(self, source):
        """
        See _remove_file_or_dir

        :param source:
        :return:
        """
        self.execute_with_host(self._remove_file_or_dir, source=source)

    def unpack_tar_to_source(self, tar_path, unpack_to):
        """
        See _unpack_tar_to_source

        :param tar_path:
        :param unpack_to:
        :return:
        """
        return self.execute_with_host(self._unpack_tar_to_source, tar_path=tar_path, unpack_to=unpack_to)

    def push_file_to_server(self, source_path, server_path):
        """
        See _push_file_to_server

        :param source_path:
        :param server_path:
        :return:
        """
        return self.execute_with_host(self._push_file_to_server, source_path=source_path, server_path=server_path)

    def create_directory(self, directory):
        """
        See _create_directory

        :param directory:
        :return:
        """
        self.execute_with_host(self._create_directory, directory=directory)

    def get_current_revision(self):
        """
        See _get_current_revision

        :return:
        """
        return_value = self.execute_with_host(self._get_current_revision).get(self.config_item.host)
        return return_value.split('/')[-1] if return_value else return_value

    def execute_with_host(self, command, *args, **kwargs):
        """
        Wrapper function to execute a function with the current host

        :param command:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return execute(command, host=self.config_item.host, *args, **kwargs)
        except Exception as exception:
            raise DeploymentException(message=unicode(exception))

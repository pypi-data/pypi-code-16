# coding: utf-8

"""DockerV - Docker helper class by Vauxoo
==========================================

This module provides a helper class to deal with docker containers in an OO way, basically wraps
`docker-py <https://github.com/docker/docker-py>`_ to deal with a json formatted configuration.

Most of the parameters can be checked in the docker official `documentation
<https://docs.docker.com/reference/run/>`_ or in the `docker-py api documentation
<http://docker-py.readthedocs.org/en/latest/api/>`_.

Still not all functionalities are implemented, but the minimal to start a docker container with
basic configuration::

    {
        "apt_install": {},
        "pip_install": {},
        "domain": "localhost",
        "command": "sleep 20",
        "env_vars": {
            "odoo_config_file": "/home/odoo/.openerp_serverrc",
            "odoo_home": "/home/odoo",
            "odoo_user": "odoo"
        },
        "image_name": "busybox",
        "mem_limit": "768m",
        "ports": {
            "8069": 8069,
            "8072": None
        },
        "remove_previous": True,
        "working_folder": "/path/to/docker_volumes",
        "volumes":{
            "filestore": "/home/odoo/.local/share/Odoo",
            "logs": "/var/log/supervisor",
            "ssh": "/home/odoo/.ssh",
            "tmp": "/tmp"
        }
    }

Where:

* *apt_install* (not implemented yet): Install additional packages using apt-get install.
    (This will be changed to use a generic way of installing packages in other distros)
* *pip_install* (not implemented yet): Install additional dependencies using pip.
* *domain*: Domain where the container will be executing.
* *image_name*: Docker image name that will be used to create the container.
    (See `official documentation <https://docs.docker.com/userguide/dockerimages/>`_)
* *mem_limit*: Max amount of ram allowed for the container.
* *ports*: A dict with ports mapping, key is the port number inside the container, value the host
    port.  If None is provided as value the port number will be assigned randomly by docker
    service.
* *remove_previous*: If there is a container with the same name or id it will be removed before
    launching the new one.
* *working_folder*: Folder in the host where the shared volumes (if any) will be created.
* *volumes*: A dict with the volume mapping, keys are the folder names inside working_folder and
    values are the actual path inside the container.
"""

import logging
from os import path
from docker import Client
import docker.errors
import simplejson as json
from deployv.helpers import container
from deployv.helpers.utils import get_error_message
from deployv.base import errors


logger = logging.getLogger('deployv')  # pylint: disable=C0103


class DockerV(object):
    """Helper class to make docker container deployments easier by code.

    If your docker service is not using the default socket you can change it by passing
    docker_url::

        config = {
            'image_name': 'busybox',
            'command': 'sleep 3',
            'mem_limit': '16m',
            'container_name': 'test_deployv',
            'ports' : {
                '8069': 8069,
                '8072': None
            },
            'env_vars': {
                'var1':'value1',
                'var2': 1234,
            }
        }
        container_object = DockerV(config)
        container_id = container_object.deploy_container()

    ``image_name`` and ``command`` are the only required parameters, others parameters are
    optional. If a port is empty, it will be autoasigned by docker.

    If the container already exists the config dict would be something like::

        config = {
            'container_name': 'test_deployv',
            'id': 'container_id'
        }

    Only one of them is needed. You can specify both, but id will be checked first then the
    container_name.
    """

    __config = {}
    __docker_id = None
    __url = None

    def __init__(self, config, timeout=300, docker_url="unix://var/run/docker.sock"):
        self.__cli = Client(base_url=docker_url, timeout=timeout)
        self.__config = config
        self.__url = docker_url
        if self.__config.get('id', False):
            inspected = self.inspect(self.__config.get('id'))
            self.__docker_id = inspected.get('Id')
        elif self.__config.get('container_name', False):
            try:
                inspected = self.inspect(self.__config.get('container_name'))
            except errors.NoSuchContainer as error:
                error_message = get_error_message(error)
                logger.debug('%s', error_message)
            else:
                self.__docker_id = inspected.get('Id')
                logger.debug('Container inspected %s',
                             json.dumps(inspected, sort_keys=True, indent=2))
                self.__config.update({'id': inspected.get('Id')})
                if not self.__config.get('image_name'):
                    self.__config.update({
                        'image_name': inspected.get('Config').get('Image')})
                if not self.__config.get('env_vars'):
                    env_vars = container.parse_env_vars(inspected.get('Config').get('Env'))
                    self.__config.update({'env_vars': env_vars})

    @property
    def url(self):
        return self.__url

    @property
    def cli(self):
        return self.__cli

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        keys = [u'image_name', u'command', ]
        if not all([key in value for key in keys]):
            raise KeyError('Mandatory keys: {}'.format(', '.join(keys)))
        self.__config = value

    @property
    def docker_id(self):
        """Returns container id, the same you see when executing 'docker ps' in the first column.

        :returns: Container Id.
        :rtype: str
        """
        return self.__docker_id.lower() if self.__docker_id else None

    @property
    def docker_env(self):
        """Gets env vars from a docker container.

        :returns: dict with var name as key and value.
        :rtype: dict
        """
        try:
            inspected = self.inspect()
        except errors.NoSuchContainer as error:
            logger.error("No such container: %s", self.docker_id)
            logger.exception(get_error_message(error))
            return None

        env_vars = inspected.get('Config').get('Env')
        res = container.parse_env_vars(env_vars)
        return res

    def deploy_container(self):
        """Deploys a container with the given config and returns some basic information about the
        container. See :func:`~deployv.base.dockerv.DockerV.basic_info` for more information about
        the format and content.

        :returns: Some basic information about the container.
        :rtype: dict
        """
        env_vars = container.generate_env_vars(self.config.get("env_vars"))
        container_name = self.config.get("container_name").lower()
        logger.debug('Deploying container %s', container_name)
        working_folder = path.join(
            self.__config.get("working_folder"),
            container_name)
        volume_binds = container.generate_binds(
            self.__config.get("volumes"), working_folder)
        volumes = container.generate_volumes(self.__config.get("volumes"))
        ports = container.generate_port_lists(self.__config.get("ports"))
        container_config = {
            "image": self.config.get("image_name"),
            "command": self.config.get("command"),
            "hostname": self.config.get("container_hostname"),
            "ports": ports,
            "environment": env_vars,
            "volumes": volumes
        }

        if self.config.get("container_name", False):
            container_config.update(
                {'name': self.config.get("container_name").lower()})
        host_config = {
            "binds": volume_binds,
            "port_bindings": self.__config.get("ports"),
            "mem_limit": self.config.get("mem_limit", 0)
        }
        if self.__config.get("remove_previous", False):
            self.__docker_id = self.config.get("container_name").lower()
            self.remove_container()
        hconfig = self.__cli.create_host_config(**host_config)
        hconfig.get('PortBindings').get("5432/tcp", [{}])[0].\
            update({'HostIp': '127.0.0.1'})
        logger.debug('Container config %s', container_config)
        try:
            container_obj = self.__cli.create_container(
                host_config=hconfig, **container_config)
            self.__docker_id = container_obj.get("Id")
            logger.debug('Created container %s', self.__docker_id)
        except docker.errors.NotFound:
            logger.exception('Image not found')
            raise errors.NoSuchImage(self.config.get("image_name"))
        except docker.errors.APIError as error:
            logger.exception('Error creating the container')
            if 'You have to remove (or rename) that container' in error.explanation:
                logger.warning('The container %s already exists, skipping create step',
                               container_config.get('name'))

        try:
            self.__cli.start(container=self.__docker_id)
        except docker.errors.APIError as error:
            if 'port is already allocated' in get_error_message(error) \
                    or 'address already in use' in get_error_message(error):
                logger.warning('Port already allocated')
                raise errors.ErrorPort(error.explanation)
        return self.basic_info

    def remove_container(self):
        """Stops and removes the specified container. Docker id or name must be in lowercase, if
        not, it will be converted to lowercase.
        """

        try:
            self.__cli.stop(self.docker_id)
            self.__cli.remove_container(self.docker_id)
        except docker.errors.NotFound as error:
            logger.debug(get_error_message(error))
        else:
            self.__docker_id = None

    @property
    def basic_info(self):
        """Gets some basic information form the container::

            {
                'Id': 'container id',
                'name': 'container name',
                'image_name': 'image used to build the container',
                'status': 'container status (same shown when "docker ps" is executed)',
                'ports': 'dict with port assignments {local (inside docker) : public}'
            }

        :returns: Container information.
        :rtype: dict
        """
        inspected = self.inspect()
        res = {}
        if inspected.get('Id') == self.docker_id:
            res.update(
                {
                    'Id': inspected.get('Id'),
                    'name': inspected.get('Name')[1:],
                    'image_name': inspected.get('Config').get('Image'),
                    'status': 'running' if inspected.get('State') else 'exited',
                    'ports': container.get_ports_dict(inspected)
                })
        return res

    def exec_cmd(self, cmd):
        """Wraps and logs the `exec_create
        <https://docker-py.readthedocs.org/en/latest/api/#exec_create>`_ and `exec_start
        <https://docker-py.readthedocs.org/en/latest/api/#exec_start>`_ methods.

        :param cmd: Command line to be executed inside the Docker container.
        :type cmd: str
        :returns: The command output.
        """
        logger.debug('exec_cmd: %s', cmd)
        try:
            exec_id = self.__cli.exec_create(self.docker_id, cmd)
        except docker.errors.APIError as error:
            if 'is not running' in error.explanation:
                raise errors.NotRunning(self.docker_id)
            raise
        res = self.__cli.exec_start(exec_id.get('Id'))
        return res

    def inspect(self, container_id=False):
        """Wrapper for docker-py.inspect _container.

        :param container_id: Optional parameter with the container name or id.
        :type container_id: str
        :returns: Information about the container.  See `inspect_container in the official docs
            <https://docker-py.readthedocs.org/en/latest/api/#inspect_container>`_.
        """
        try:
            res = self.cli.inspect_container(container_id if container_id else self.docker_id)
        except docker.errors.NotFound:
            raise errors.NoSuchContainer(container_id if container_id else self.docker_id)
        except docker.errors.NullResource:
            raise errors.NoSuchContainer(container_id if container_id else self.docker_id)
        return res

    def install_packages(self, apt_packages=None, pip_packages=None):
        """Installs apt and/or pip packages inside the container and returns the full operation
        log. Runs quietly, so the log is cleaner.

        The result has the following format (if no errors were found)::

            {
                'apt_install': [
                    {
                        'package_name': {
                            'installed': True
                        }
                    }
                ]
                'pip_install': [
                    {
                        'package_name': {
                            'installed': True
                        }
                    }
                ]
            }

        In case of error::

            {
                'apt_install': [
                    {
                        'package_name': {
                            'installed': False,
                            'message': 'Error msg generated by the installer'
                        }
                    }
                ]
                'pip_install': [
                    {
                        'package_name': {
                            'installed': False,
                            'message': 'Error msg generated by the installer'
                        }
                    }
                ]
            }

        The results can be mixed if some packages fail and some don't during the installation
        process.

        :param apt_packages: Packages to be installed via apt.
        :type apt_packages: list
        :param pip_packages: Packages to be installed via pip.
        :type pip_packages: list
        :returns: Full log operations.
        :rtype: dict
        """
        res = {}
        if isinstance(apt_packages, list) and apt_packages:
            self.exec_cmd('apt-get update -q')
            res.update({'apt_install': []})
            for apt_package in apt_packages:
                cmd_res = self.exec_cmd('apt-get install {name} -yq'.format(name=apt_package))
                logger.debug('apt_install %s', cmd_res)
                composed = self._compose_message('apt_install', apt_package, cmd_res)
                res.get('apt_install').append(composed)

        if isinstance(pip_packages, list) and pip_packages:
            res.update({'pip_install': []})
            for pip_package in pip_packages:
                cmd_res = self.exec_cmd('pip install {name}'.format(name=pip_package))
                logger.debug('pip_install %s', cmd_res)
                composed = self._compose_message('pip_install', pip_package, cmd_res)
                res.get('pip_install').append(composed)
        return res

    def _compose_message(self, package_installer, package, result):
        """Composes the response.

        The response has the following format::

            {
                'package_name': {
                    'installed': Boolean,
                    'message': 'if any error, this will have the error msg.'
                               'if no error, this won't be present.'
                }
            }

        :param package_installer: Package installer name (so far pip or apt).
        :type package_installer: str
        :param package: Package/dependency installed.
        :type package: string.
        :param result: The result from :meth:`~deployv.base.dockerv.DockerV.exec_cmd`.
        :returns: Formatted output in a json format.
        :rtype: dict
        """
        res = {package: {}}
        errors_txt = ['Unable to locate package', 'No matching distribution found']
        if any([error_txt in result for error_txt in errors_txt]):
            res.get(package).update(
                {
                    'installed': False,
                    'message': result
                })
        else:
            res.get(package).update({'installed': True})
        return res

    def pull(self, image_name):
        """This is a simple wrapper for docker pull to use the deployv exceptions instead of the
        docker ones.

        :param image_name: The image name to pull.
        :type image_name: str
        """
        try:
            self.cli.pull(image_name)
        except docker.errors.NotFound:
            raise errors.NoSuchImage(image_name)

    def inspect_image(self, image_name):
        """Wrapper for the inspect image, basically does the same but raises a deployv exception
        instead of the docker-py one.

        :param image_name: The image name that will be inspected.
        :type image_name: str
        :returns: The result of docker inspect_image.
        :raises: :class:`~deployv.base.errors.NoSuchImage` if the image doesn't exist.
        """
        try:
            res = self.cli.inspect_image(image_name)
        except docker.errors.NotFound:
            raise errors.NoSuchImage(image_name)
        return res

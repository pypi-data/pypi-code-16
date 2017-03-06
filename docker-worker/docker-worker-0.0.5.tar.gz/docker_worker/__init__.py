from __future__ import absolute_import

import base64
import logging
import os
import pipes
import sys
import threading
import uuid
import time, random

import docker
import six.moves.urllib.parse as urlparse
from gym.utils import closer
from docker_worker import error, utils
# imported from universe
from docker_worker.compose import container, log_printer, progress_stream

# docker.Client got renamed to APIClient in 2.2
if hasattr(docker, 'APIClient'):
    docker_client = docker.APIClient
else:
    docker_client = docker.Client

logger = logging.getLogger(__name__)

docker_closer = closer.Closer()

def start_logging(instances):
    containers = [instance._container for instance in instances]
    labels = [str(instance.label) for instance in instances]
    if all(instance.reusing for instance in instances):
        # All containers are being reused, so only bother showing
        # a subset of the backlog.
        tail = 0
    else:
        # At least one container is new, so just show
        # everything. It'd be nice to have finer-grained control,
        # but this would require patching the log printer.
        tail = 'all'
    log_printer.build(containers, labels, log_args={'tail': tail})

def random_alphanumeric(length=14):
    buf = []
    while len(buf) < length:
        entropy = base64.encodestring(uuid.uuid4().bytes).decode('utf-8')
        bytes = [c for c in entropy if c.isalnum()]
        buf += bytes
    return ''.join(buf)[:length]

def pretty_command(command):
    return ' '.join(pipes.quote(c) for c in command)

def get_client():
    info = {}
    host = os.environ.get('DOCKER_HOST')

    client_api_version = os.environ.get('DOCKER_API_VERSION')
    if not client_api_version:
        client_api_version = "auto"

    # IP to use for started containers
    if host:
        info['host'] = urlparse.urlparse(host).netloc.split(':')[0]
    else:
        info['host'] = 'localhost'

    verify = os.environ.get('DOCKER_TLS_VERIFY') == '1'
    if verify: # use TLS
        assert_hostname = None
        cert_path = os.environ.get('DOCKER_CERT_PATH')
        if cert_path:
            client_cert = (os.path.join(cert_path, 'cert.pem'), os.path.join(cert_path, 'key.pem'))
            ca_cert = os.path.join(cert_path, 'ca.pem')
        else:
            client_cert = ca_cert = None

        tls_config = docker.tls.TLSConfig(
            client_cert=client_cert,
            ca_cert=ca_cert,
            verify=verify,
            assert_hostname=assert_hostname,
        )
        return docker_client(base_url=host, tls=tls_config, version=client_api_version), info
    else:
        return docker_client(base_url=host, version=client_api_version), info

class PortAssigner(object):
    _instances = 0

    def __init__(self, prefix='worker', reuse=False):
        self.reuse = reuse
        self._next_port = 10000
        self.i = -1
        self.lock = threading.RLock()
        self.ports = None
        self.instance_id = prefix + random_alphanumeric(length=6)
        self.client = None
        self.info = None

    def populate_once(self):
        with self.lock:
            self.client, self.info = get_client()
            if self.ports is None:
                self.refresh_ports()

    def next_instance_num(self):
        with self.lock:
            type(self)._instances += 1
            return type(self)._instances

    def refresh_ports(self):
        ports = {}
        for container in self.client.containers():
            for port in container['Ports']:
                # {u'IP': u'0.0.0.0', u'Type': u'tcp', u'PublicPort': 5000, u'PrivatePort': 500}
                if port['Type'] == 'tcp' and 'PublicPort' in port:
                    ports[port['PublicPort']] = container['Id']
        self.ports = ports

    def allocate_ports(self, num):
        with self.lock:
            return self._allocate_ports(num)

    def _allocate_ports(self, num):
        ports = []
        if self.reuse and self._next_port in self.ports:
            assert False

            # vnc_id = self.ports[self._next_port]
            # rewarder_id = self.get(self._next_port+10000)

            # # Reuse an existing docker container if it exists
            # if (self._next_port+10000) not in self.shared_state:
            #     raise error.Error("Port {} was allocated but {} was not. This indicates unexpected state with spun-up VNC docker instances.".format(self._next_port, self._next_port+1))
            # elif vnc_id != rewarder_id:
            #     raise error.Error("Port {} is exposed from {} while {} is exposed from {}. Both should come from a single Docker instance running your environment.".format(vnc_id, self._next_port, rewarder_id, self._next_port+10000))

            # base = self._next_port
            # self._next_port += 1
            # return base, vnc_id
        elif not self.reuse:
            # Otherwise, allocate find the lowest free ports. This
            # doesn't work for the reuse case since on restart we
            # won't remember where we spun up our containers.
            for _ in range(num):
                while self._next_port in self.ports:
                    self._next_port += 1
                ports.append(self._next_port)
                self._next_port += 1

        # And get started!
        return ports, None

class Manager(object):
    assigner = PortAssigner()

    def __init__(self, image, cmd=[], n=1, ports=[], cap_add=[], volumes=[], enable_logging=True):
        self.image = image
        self.cmd = cmd
        self.n = n
        self.internal_ports = ports
        self.cap_add = cap_add
        self.volumes = volumes
        self.enable_logging = enable_logging

        self.instances = []

        # We are ourselves inside docker! This is important for
        # networking: inside docker, we'll assume we can reach docker
        # IPs directly. Outside docker, if using a socket the IP
        # address of the docker host is localhost.
        self.is_inside_docker = os.path.exists('/.dockerenv')

        # Make sure this has been refreshed
        self.assigner.populate_once()

        self._start()

    def _start(self):
        if len(self.instances) > 0:
            raise error.Error('Already started. Manager does not currently support dynamically spinning up instances.')

        for _ in range(self.n):
            instance = DockerInstance(self.assigner, self.image, label=self.assigner.next_instance_num(), internal_ports=self.internal_ports, cap_add=self.cap_add, cmd=self.cmd, is_inside_docker=self.is_inside_docker)
            self.instances.append(instance)

        [instance.start() for instance in self.instances]

        if self.enable_logging:
            start_logging(self.instances)

        return self.instances

    def wait(self):
        start = time.time()

        while True:
            keep_waiting = 0
            for instance in self.instances:
                if instance.booted():
                    continue
                keep_waiting += 1
                instance.healthcheck(logs=True)
                time.sleep(1)
                delta = time.time() - start
                if delta > 120:
                    raise error.Error('{} did not boot in {}'.format(instance.label, delta))
            if keep_waiting == 0:
                break

    def close(self):
        [instance.close() for instance in self.instances]

class DockerInstance(object):
    def __init__(self, assigner, image, cmd=[], internal_ports=[], cap_add=[], volumes=[], label='main', is_inside_docker=False):
        self._docker_closer_id = docker_closer.register(self)

        self.label = label
        self.assigner = assigner
        self.name='{}-{}'.format(self.assigner.instance_id, self.label),

        self.image = image
        self.cmd = cmd
        self.internal_ports = internal_ports
        self.cap_add = cap_add
        self.volumes = volumes

        self.container_ip = None
        self._container_id = None
        self._closed = False

        self._container = None

        self._is_inside_docker = is_inside_docker
        self.external_host = self.assigner.info['host']

        self.ports = {}
        self.reusing = None
        self.started = False

    def healthcheck(self, logs=False):
        current = container.Container.from_id(self.client, self._container_id)
        if current.is_running:
            return
        if logs:
            raise error.Error('Container {} is not running: exit_code={} logs={}'.format(self._container_id, current.exit_code, current.logs()))
        else:
            raise error.Error('Container {} is not running: exit_code={}'.format(self._container_id, current.exit_code))

    def booted(self):
        if self._is_inside_docker:
            return utils.port_open(self.container_ip, self.internal_ports[0])
        else:
            return utils.port_open(self.external_host, self.external_ports[0])

    def start(self, attempts=None):
        if attempts is None:
            # If we're reusing, we don't scan through ports for a free
            # one.
            if not self.assigner.reuse:
                attempts = 20
            else:
                attempts = 1

        for attempt in range(attempts):
            self._spawn()
            e = self._start()
            if e is None:
                return

            time.sleep(random.uniform(1.0, 5.0))
            self.assigner.refresh_ports()

        raise error.Error('[{}] Could not start container after {} attempts. Last error: {}'.format(self.label, attempts, e))

    def _spawn(self):
        with self.assigner.lock:
            self.__spawn()

    def __spawn(self):
        if self.image is None:
            raise error.Error('No image specified')
        assert self._container_id is None

        self.external_ports, self._container_id = self.assigner.allocate_ports(len(self.internal_ports))
        for external, internal in zip(self.external_ports, self.internal_ports):
            self.ports[internal] = external

        if self._container_id is not None:
            logger.info('[%s] Reusing container %s: ports=%s', self.label, self._container_id[:12], ports)
            self.reusing = True
            self.started = True
            return

        port_args = []
        for external, internal in zip(self.external_ports, self.internal_ports):
            port_args += ['-p', '{}:{}'.format(external, internal)]
        volume_args = []
        for volume in self.volumes:
            volume_args += ['-v', volume]
        cap_add_args = []
        for cap in self.cap_add:
            cap_add_args += ['--cap-add', cap]

        self.reusing = False
        logger.info('[%s] Creating container: image=%s. Run the same thing by hand as: %s',
                    self.label,
                    self.image,
                    pretty_command([
                        'docker', 'run', '--rm'
                    ] + port_args + cap_add_args + [
                        self.image
                    ] + self.cmd))
        try:
            container = self._spawn_container()
        except docker.errors.NotFound as e:
            # Looks like we need to pull the image
            explanation = e.explanation
            if isinstance(explanation, bytes):
                explanation = explanation.decode('utf-8')
            assert 'No such image' in explanation, 'Expected NotFound error message message to include "No such image", but it was: {}. This is probably just a bug in this assertion and the assumption was incorrect'.format(explanation)

            logger.info('Image %s not present locally; pulling', self.image)
            self._pull_image()
            # If we called pull_image from multiple processes (as we do with universe-starter-agent A3C)
            # these will all return at the same time. We probably all got the same port numbers before the pull started,
            # so wait a short random time and refresh our port numbers
            time.sleep(random.uniform(0.5, 2.5))
            self.assigner.refresh_ports()
            self.extrenal_ports, self._container_id = self.assigner.allocate_ports(1)
            if self._container_id is not None:
                logger.info('[%s] Reusing container %s: ports=%s', self.label, self._container_id[:12], self.external_ports)
                self.reusing = True
                self.started = True
                return
            # Try spawning again.
            container = self._spawn_container()

        self._container_id = container['Id']

    def _pull_image(self):
        output = self.client.pull(self.image, stream=True)
        return progress_stream.get_digest_from_pull(
            progress_stream.stream_output(output, sys.stdout))

        # docker-compose uses this:
        # try:
        # except StreamOutputError as e:
        #     if not ignore_pull_failures:
        #         raise
        #     else:
        #         log.error(six.text_type(e))

    def _spawn_container(self):
        # Ports
        ports = []
        for external, internal in zip(self.external_ports, self.internal_ports):
            # e.g. "1234/udp", 1234, "1234/tcp"
            spec = str(internal).split('/')
            if len(spec) == 1:
                spec.append('tcp')
            ports.append(spec)

        # Volumes
        volumes = [v.split(':')[1] for v in self.volumes]

        # launch instance, and refresh if error
        container = self.client.create_container(
            image=self.image,
            command=self.cmd,
            # environment=self.runtime.environment,
            name=self.name,
            ports=ports,
            volumes=volumes,
            host_config=self.client.create_host_config(
                port_bindings=self.ports,
                cap_add=self.cap_add,
                binds=self.volumes,
            ),
            labels={
                'com.openai.automanaged': 'true',
            },
            cpu_shares=1024,
        )
        return container

    def _start(self):
        # Need to start up the container!
        if not self.started:
            logger.debug('[%s] Starting container: id=%s', self.label, self._container_id)
            try:
                self.client.start(container=self._container_id)
            except docker.errors.APIError as e:
                if 'port is already allocated' in str(e.explanation):
                    logger.info('[%s] Could not start container: %s', self.label, e)
                    self._remove()
                    return e
                else:
                    raise
            else:
                self._container = container.Container.from_id(self.client, self._container_id)
                self.container_ip = self.client.inspect_container(self._container_id)['NetworkSettings']['IPAddress']
                self.started = True

        return None

    def _remove(self):
        logger.info("Killing and removing container: id=%s image=%s", self._container_id, self.image)
        try:
            self.client.remove_container(container=self._container_id, force=True)
        except docker.errors.APIError as e:
            # This seems to happen occasionally when we try to delete a container immediately after creating it.
            # But although we get an error trying to remove it, it usually goes away shortly
            # A typical error message is
            #   Driver aufs failed to remove root filesystem 0015803583d91741d25fce28ae0ef540b436853d1c90061caacaef97e3682403: \
            #   rename /var/lib/docker/aufs/mnt/69a72854511f1fbb9d7cb0ef0ce0787e573af0887c1213ba3a0c3a0cfd71efd2 \
            #   /var/lib/docker/aufs/mnt/69a72854511f1fbb9d7cb0ef0ce0787e573af0887c1213ba3a0c3a0cfd71efd2-removing: \
            #   device or resource busy
            # Just proceed as if it had gone away
            if 'device or resource busy' in str(e.explanation):
                logger.info("[%s] Could not remove container: %s. You can always kill all automanaged environments on this Docker daemon via: docker rm -f $(docker ps -q -a -f 'label=com.openai.automanaged=true')", self.label, e)
                self._container_id = None
                return e
            else:
                raise

        self._container_id = None

    def __del__(self):
        self.close()

    def close(self):
        if self._closed:
            return

        docker_closer.unregister(self._docker_closer_id)

        # Make sure 1. we were the onse who started it, 2. it's
        # actually been started, and 3. we're meant to kill it.
        if self._container_id and not self.assigner.reuse:
            self._remove()

        self._closed = True

    @property
    def client(self):
        return self.assigner.client

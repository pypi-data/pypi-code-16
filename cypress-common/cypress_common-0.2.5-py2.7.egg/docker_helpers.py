import socket
import time
import traceback
import docker

REPO = "cypress-registry.istuary.co:5000"
TEST_NETWORK = "test_cypress_common_network"
TEST_KAFKA_IMG = 'kafka'
TEST_ZK_IMG = 'zookeeper'
TEST_REDIS_IMG = 'redis'
TEST_ENGINE_MANAGER_IMG = "engine_manager"
TEST_SEARCH_ENGINE_IMG = "search_engine_simulator"
TEST_ENGINE_IMG = "cypress_engine_gpu"
TEST_ACMW_IMG = "cypress-ac_mw"
TAG = "latest"
NVIDIA_DOCKER_URL = '/v1.0/docker/cli/json?dev=0'

__cli = docker.APIClient(base_url='unix://var/run/docker.sock')
# __cli = docker.from_env()


def get_host_real_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

REAL_IP = get_host_real_ip()


# Setup AC MW Test Environment, create docker virtual networks, containers and volumes for testing
def setup_docker(mw__containers=None):
    if not mw__containers:
        mw__containers = {
            'ac_mw': None,
            'zookeeper': None,
            'kafka': None,
            'redis': None,
            'search_engine': None
        }
    __containers = mw__containers
    __test_network = create_network_if_not_exist(__cli, name=TEST_NETWORK)
    # remove all old containers
    [remove_old_containers(__cli, name=n) for n in __containers.iterkeys()]

    create_cluster_class = CreateCluster(__cli, TEST_NETWORK)
    for img_name in __containers:
        if "zookeeper" == img_name:
            continue
        create_cluster = getattr(create_cluster_class, "create_{}_cluster".format(img_name))

        cluster = create_cluster()

        if len(cluster) == 0:
            raise RuntimeError("Failed to create {} cluster".format(img_name))

        for k in cluster.keys():
            __containers[k] = cluster[k]

    pull_all_images()

    try:
        # start containers
        [__cli.start(container=c.get('Id')) for c in __containers.itervalues()]

        # print __cli.info()

        for c in __containers.itervalues():
            print(__cli.inspect_container(container=c.get('Id')))

        time.sleep(10.0)  # requires 10 seconds to let Zookeeper and Kafka server to get ready
    except Exception as e:
        print e
        traceback.print_exc()
        tear_down_docker()
        raise Exception("Test setup failure. {0}".format(e))


def pull_all_images():
    images_list = [var for var in dir() if var[0:4] == "TEST" and var[-4:] == "_IMG"]
    [__cli.pull('/'.join([REPO, c]), "latest") for c in images_list]


# Tear down test environment.
def tear_down_docker():
    global __containers
    try:
        for container in __containers.values():
            try:
                __cli.stop(container=container.get('Id'), timeout=10.0)
                __cli.remove_container(container=container.get('Id'))
            except Exception as e:
                print e
    except Exception as ex:
        print ex

    finally:
        # clean up test network
        remove_old_test_network(__cli, name=TEST_NETWORK)


class CreateCluster(object):
    def __init__(self, client, network=TEST_NETWORK):
        """
            Create a redis cluster in container.
            :param client: docker client
            :type client: docker.Client
            :param network: docker network which the containers will connect to.
            :type network: basestring
            :return: a dictionary of the containers i.e. {'redis': <container>}
        """
        self.client = client
        self.network = network

    def create_kafka_cluster(self):
        cluster = dict()
        cluster["zookeeper"] = self.client.create_container(
            image='/'.join([REPO, TEST_ZK_IMG]),
            name="zookeeper",
            hostname="zookeeper",
            ports=[2181],
            host_config=self.client.create_host_config(port_bindings={
                2181: 2181
            }),
            networking_config=self.client.create_networking_config({
                str(self.network): self.client.create_endpoint_config(
                    aliases=['zk', 'zookeeper'])
            })
        )

        print("Host address is {0}".format(get_host_real_ip()))

        cluster['kafka'] = self.client.create_container(
            image='/'.join([REPO, TEST_KAFKA_IMG]),
            name="kafka",
            hostname="kafka",
            ports=[9092],
            environment=dict(KAFKA_ADVERTISED_HOST_NAME=REAL_IP,
                             KAFKA_ADVERTISED_PORT=9092,
                             KAFKA_ZOOKEEPER_CONNECT="{}:2181".format(REAL_IP)),
            volumes=["/var/run/docker.sock:/var/run/docker.sock"],
            networking_config=self.client.create_networking_config({
                str(self.network): self.client.create_endpoint_config(links=[('zookeeper', 'zookeeper')])}),
            host_config=self.client.create_host_config(
                port_bindings={9092: 9092}
            ))
        return cluster

    def create_redis_cluster(self):
        cluster = dict()
        cluster['redis'] = self.client.create_container(
            image='/'.join([REPO, TEST_REDIS_IMG]),
            name="redis",
            hostname="redis",
            networking_config=self.client.create_networking_config({
               str(self.network): self.client.create_endpoint_config(aliases=['redis'])}),

            ports=[6379],
            host_config=self.client.create_host_config(port_bindings={
                6379: 6379
            }))
        return cluster

    def create_enginemanager_cluster(self):
        cluster = dict()
        cluster['enginemanager'] = self.client.create_container(
            image='/'.join([REPO, TEST_ENGINE_MANAGER_IMG]),
            name='enginemanager',
            hostname="enginemanager",
            environment={
                "KAFKA": "{0}:9092".format(REAL_IP),
                "REDIS": REAL_IP,
                "HOST_IP": REAL_IP
            },
            networking_config=self.client.create_networking_config({
                str(self.network): self.client.create_endpoint_config(links=[('kafka', 'kafka'), ('redis', 'redis'), ('zookeeper', 'zookeeper')])}),
            volumes=["/var/run/docker.sock:/var/run/docker.sock", "./engines.yaml:/usr/local/etc/cypress/config.yaml"],
            host_config=self.client.create_host_config(
                privileged=True),
            command=['/root/start_manager.py', '--kafka=kafka:9092', '--redis={}'.format(REAL_IP)]
        )
        return cluster

    def create_searchengine_cluster(self):
        cluster = dict()
        cluster['searchengine'] = self.client.create_container(
            image='/'.join([REPO, TEST_SEARCH_ENGINE_IMG]),
            name='searchengine',
            hostname="searchengine",
            environment={
                "KAFKA": "{0}:9092".format(REAL_IP),
                "REDIS": REAL_IP
            },
            networking_config=self.client.create_networking_config({
                str(self.network): self.client.create_endpoint_config(
                    links=[('kafka', 'kafka'), ('redis', 'redis'), ('zookeeper', 'zookeeper')])})
        )
        return cluster

    def create_acmw_cluster(self):
        cluster = dict()
        cluster['acmw'] = self.client.create_container(
            image='/'.join([REPO, TEST_ACMW_IMG]),
            name="acmw",
            hostname="acmw",
            networking_config=self.client.create_networking_config({
                str(self.network): self.client.create_endpoint_config(aliases=['acmw'])}),

            ports=[5001],
            host_config=self.client.create_host_config(port_bindings={
                5001: 5001
            }))
        return cluster


def create_network_if_not_exist(client, name=TEST_NETWORK):
    """
    Create a test network if the test network doesn't exist.
    :param client: docker client
    :type client: docker.Client
    :param name: network name
    :type name: basestring
    :return network object; if the network exists, return the existing network object.
    """
    networks = client.networks(names=[name])
    if len(networks) == 0:
        network = client.create_network(name, driver="bridge", internal=False)
    else:
        network = networks[0]

    return network


def remove_old_containers(client, name):
    """
    Stop and remove containers with a give name.
    :param client: docker client
    :type client: docker.Client
    :param name: container name
    :type name: basestring
    """
    ids = map(lambda c: c.get('Id'), client.containers(all=True, filters={"name": name}))

    [client.remove_container(container=i, v=True, force=True) for i in ids]


# delete all all old test networks
def remove_old_test_network(client, name=TEST_NETWORK):
    """
    Remove old test networks to avoid name conflict.
    :param client: Docker Client object
    :type client: docker.Client
    :param name: name of the network to be deleted. Default: TEST_NETWORK
    :type name: basestring
    """
    for n in client.networks(names=[name]):
        # print(n)
        [client.remove_container(container=i, v=True, force=True) for i in n["Containers"].keys()]
        client.remove_network(n.get('Id'))

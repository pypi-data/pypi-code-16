from plato_clean.cases import get_resource
from plato_clean.cases import wait_busy_resource
from plato_clean.cases import post_resource


class CleanNetworks():

    def run(self, API, sleep):
        port_forwardings = get_resource(API, 'DescribePortForwardings', {
            'status': ['active']
        }, 'portForwardingSet')

        port_forwarding_ids = [i['portForwardingId']
                               for i in port_forwardings]

        post_resource(API, 'DeletePortForwardings',
                      port_forwarding_ids, 'portForwardingIds')

        wait_busy_resource(API, 'DescribeNetworks', {
            'status': ['pending', 'building'],
        }, sleep)

        networks = get_resource(API, 'DescribeNetworks', {
            'status': ['active', 'disabled', 'error']
        }, 'networkSet')

        network_ids = [n['networkId']
                       for n in networks if n['externalGatewayIp']]

        # unset external gateway
        post_resource(API, 'UnsetExternalGateway',
                      network_ids, 'networkIds')

        subnets = get_resource(API, 'DescribeSubnets', {
            'status': ['active']
        }, 'subnetSet')

        subnet_ids = [i['subnetId'] for i in subnets]

        post_resource(API, 'DeleteSubnets', subnet_ids, 'subnetIds')

        # delete networks
        network_ids = [n['networkId'] for n in networks]
        post_resource(API, 'DeleteNetworks', network_ids, 'networkIds')

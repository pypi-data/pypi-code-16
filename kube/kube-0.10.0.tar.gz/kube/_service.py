"""Interface for Service resources."""

import ipaddress

from kube import _base
from kube import _error


API_PATHS = ['api/v1']


class ServiceView(_base.BaseView, _base.ViewABC):
    """View of the Service resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.ServiceList
    resource = 'services'
    api_paths = API_PATHS


class ServiceItem(_base.BaseItem, _base.ItemABC):
    """A Service in the Kubernetes cluster.

    :param cluster: The cluster this Service exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.Service
    resource = 'services'
    api_paths = API_PATHS

    @property
    def loadbalancer_ingress(self):
        """The load balancer ingress endpoints.

        This is a set of ingress endpoints in use by the
        load balancer.  Depending on the infrastructure the cluster
        runs on the endpoint can be either an
        :class:`ipaddress.IPv4Address`, :class:`ipaddress.IPv6Address`
        or a hostname as a string.
        """
        try:
            ingress = self.raw['status']['loadBalancer']['ingress']
        except KeyError:
            raise _error.StatusError
        endpoints = set()
        for endpoint in ingress:
            if 'ip' in endpoint:
                endpoints.add(ipaddress.ip_address(endpoint['ip']))
            elif 'hostname' in endpoint:
                endpoints.add(endpoint['hostname'])
            else:
                raise _error.StatusError
        return endpoints

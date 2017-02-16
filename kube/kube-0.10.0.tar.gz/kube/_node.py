"""Interface for node resources."""

import collections
import enum
import ipaddress

from kube import _base
from kube import _error
from kube import _util


API_PATHS = ['api/v1']


class NodeView(_base.BaseView, _base.ViewABC):
    """View of all the Node resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.  This is here for the :class:`kube.ViewABC`
       compatibility but can not be used for the NodeList resource.  A
       :class:`kube.NamespaceError` is raised when this is not
       ``None``.
    :type namespace: NoneType

    :raises kube.NamespaceError: If instantiated using a namespace.

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.

    :ivar cluster: The :class:`kube.Cluster` instance.
    """
    kind = _base.Kind.NodeList
    resource = 'nodes'
    api_paths = API_PATHS

    def __init__(self, cluster, namespace=None):
        if namespace is not None:
            raise _error.NamespaceError('NodeView does not support namespaces')
        super().__init__(cluster, None)

    def fetch(self, name, namespace=None):
        """Retrieve an individual node by name.

        This returns the current verison of the resource item.

        :param str name: The name of the node to retrieve.
        :param str namespace: Must be *None* or a
           :class:`kube.NamespaceError` is raised.  Here only for
           compatibility with the ABC.

        :return: A single :class:`kube.NodeItem` instance.
        :raises LookupError: If the node does not exist.
        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.NamespaceError: If a namespace is used.
        """
        if namespace is not None:
            raise _error.NamespaceError('NodeView does not support namespaces')
        data = _util.fetch_resource(self.cluster, self.api_path, 'nodes', name)
        return NodeItem(self.cluster, data)


class AddressType(enum.Enum):
    """Enumeration of the address types."""
    ExternalIP = 'ExternalIP'
    InternalIP = 'InternalIP'
    Hostname = 'Hostname'
    LegacyHostIP = 'LegacyHostIP'


class NodeItem(_base.BaseItem, _base.ItemABC):
    """A node in the Kubernetes cluster.

    See http://kubernetes.io/docs/admin/node/ for details.

    :param cluster: The cluster this node belongs to.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.Node
    resource = 'nodes'
    api_paths = API_PATHS
    _Address = collections.namedtuple('Address', ['type', 'addr'])

    @property
    def addresses(self):
        """An iterator of the addresses for this node.

        Each address is a namedtuple with ``(type, addr)`` as fields.
        Known types are in the :class:`kube.AddressType` enumeration.

        An empty list is returned if there are not yet any addresses
        associated with the node.

        According to the K8s API spec (and K8s code) the node address
        array may contain addresses of the types defined by
        ``kube.AddressType``.  The ``Hostname`` address type, while unlikely,
        may present itself for certain cloud providers and will contain a
        hostname string, not an IP address.
        """
        status = self.raw.get('status', {})
        for raw in status.get('addresses', []):
            type_ = AddressType(raw['type'])
            try:
                addr = ipaddress.ip_address(raw['address'])
            except ValueError as err:
                if type_ is AddressType.Hostname:
                    addr = raw['address']
                else:
                    raise err
            yield self._Address(type_, addr)

    @property
    def capacity(self):
        """The capacity of the node.

        CPU is expressed in cores and can use fractions of cores,
        while memory is expressed in bytes.
        """
        # See http://kubernetes.io/v1.1/docs/design/resources.html for
        # details on resources usage.  This needs to deal with custom
        # resources as well.  The current stub implementation does not
        # match well.
        raise NotImplementedError

    @property
    def conditions(self):
        """List of conditions."""
        raise NotImplementedError

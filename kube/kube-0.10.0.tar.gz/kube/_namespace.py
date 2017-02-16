"""Interface for namespaces."""

import enum

from kube import _base
from kube import _error
from kube import _util


API_PATHS = ['api/v1']


class NamespaceView(_base.BaseView, _base.ViewABC):
    """View of all the Namespace resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.  This is here for the :class:`kube.ViewABC`
       compatibility, namespaces can not be used for the NamespaceList
       resource.  A :class:`kube.NamespaceError` is raised when this
       is not ``None``.
    :type namespace: NoneType

    :raises kube.NamespaceError: If instantiated using a namespace.

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.NamespaceList
    resource = 'namespaces'
    api_paths = API_PATHS

    def __init__(self, cluster, namespace=None):
        if namespace is not None:
            raise _error.NamespaceError(
                'NamespaceList does not support namespaces')
        super().__init__(cluster, None)

    def fetch(self, name, namespace=None):
        """Retrieve an individual Namespace resource item by name.

        This returns the current version of the resource item.

        :param str name: The name of the namespace resource item to
           retrieve.
        :param str namespace: Must be *None* or a
           :class:`kube.NamespaceError` is raised.  Here only for
           compatibility with the ABC.

        :returns: A :class:`kube.NamespaceItem` instance.
        :raises LookupError: If the namespace does not exist.
        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.NamespaceError: If a namespace is used.
        """
        if namespace is not None:
            raise _error.NamespaceError(
                'NamespaceView does not support namespaces')
        data = _util.fetch_resource(self.cluster,
                                    self.api_path, 'namespaces', name)
        return NamespaceItem(self.cluster, data)


class NamespacePhase(enum.Enum):
    """Enumeration of all possible namespace phases.

    This is aliased to :attr:`NamespaceResource.NamespacePhase`
    for convenience.
    """
    Active = 'Active'
    Terminating = 'Terminating'


class NamespaceItem(_base.BaseItem, _base.ItemABC):
    """A namespace in the Kubernetes cluster.

    See http://kubernetes.io/docs/admin/namespaces/ for details.

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    :cvar NamespacePhase: Convenience alias of :class:`NamespacePhase`.
    """
    kind = _base.Kind.Namespace
    resource = 'namespaces'
    api_paths = API_PATHS
    NamespacePhase = NamespacePhase

    def delete(self):
        """Delete the namespace resource item.

        For Namespace deletion K8s may have some work to do and could
        return a 409 (Conflict) instead of a 404 (Not Found) when a
        subsequent delete call occurs while status is trying to catch
        up with spec.  We hide this idiosyncrasy from the kube user.

        :rtype: None

        :raises APIError: For errors from the k8s API server.
        """
        try:
            super().delete()
        except _error.APIError as err:
            if err.status_code != 409:
                raise

    @property
    def phase(self):
        """Phase of the namespace as a :class:`kube.NamespacePhase`."""
        return NamespacePhase(self.raw['status']['phase'])

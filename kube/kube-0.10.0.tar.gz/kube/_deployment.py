"""Interface for Deployment resources.

These used to be called ReplicationController before.
"""

from kube import _base
from kube import _util


API_PATHS = ['apis/extensions/v1beta1']


class DeploymentView(_base.BaseView, _base.ViewABC):
    """View of the Deployment resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.DeploymentList
    resource = 'deployments'
    api_paths = API_PATHS


class DeploymentItem(_base.BaseItem, _base.ItemABC):
    """A Deployment in the Kubernetes cluster.

    A Deployment provides declarative updates for Pods and Replica Sets.

    :param cluster: The cluster this Deployment exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.Deployment
    resource = 'deployments'
    api_paths = API_PATHS

    @_util.statusproperty
    def observed_generation(self):
        """The (integer) generation of the Deployment."""
        return self.raw['status']['observedGeneration']

    @_util.statusproperty
    def observed_replicas(self):
        """Total number of non-terminated pods targeted by this deployment."""
        return self.raw['status']['replicas']

    @_util.statusproperty
    def updated_replicas(self):
        """Nr. of non-terminated pods targeted with desired template spec."""
        return self.raw['status']['updatedReplicas']

    @_util.statusproperty
    def available_replicas(self):
        """Number of available pods ready for at least minReadySeconds."""
        return self.raw['status']['availableReplicas']

    @_util.statusproperty
    def unavailable_replicas(self):
        """Total number of unavailable pods targeted by this deployment."""
        return self.raw['status']['unavailableReplicas']

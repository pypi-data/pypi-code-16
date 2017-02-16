"""Interface for Replication Controller resources."""

from kube import _base
from kube import _util


API_PATHS = ['api/v1']


class ReplicationControllerView(_base.BaseView, _base.ViewABC):
    """View of the Replication Controller resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.ReplicationControllerList
    resource = 'replicationcontrollers'
    api_paths = API_PATHS


class ReplicationControllerItem(_base.BaseItem, _base.ItemABC):
    """A Replication Controller in the Kubernetes cluster.

    A ReplicationController, is responsible for keeping a desired number of
    pods running.

    :param cluster: The cluster this Replication Controller exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.ReplicationController
    resource = 'replicationcontrollers'
    api_paths = API_PATHS

    @_util.statusproperty
    def observed_replicas(self):
        """The current number of replicas observed."""
        return self.raw['status']['replicas']

    @_util.statusproperty
    def observed_generation(self):
        """The (integer) generation of the ReplicaSet."""
        return self.raw['status']['observedGeneration']

    @_util.statusproperty
    def fully_labeled_replicas(self):
        """Number of pods which have an exact matching set of labels.

        This counts the pods which have the exact same set of labels
        as the labelselector of this replication controller.
        """
        return self.raw['status']['fullyLabeledReplicas']

    @_util.statusproperty
    def ready_replicas(self):
        """The number of ready replicas for the ReplicaSet."""
        return self.raw['status']['readyReplicas']

    @_util.statusproperty
    def available_replicas(self):
        """The number of available replicas (ready for at least
        minReadySeconds) for the ReplicaSet."""
        return self.raw['status']['availableReplicas']

"""Interface for DaemonSet resources."""

from kube import _base
from kube import _util


API_PATHS = ['apis/extensions/v1beta1']


class DaemonSetView(_base.BaseView, _base.ViewABC):
    """View of the DaemonSet resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.DaemonSetList
    resource = 'daemonsets'
    api_paths = API_PATHS


class DaemonSetItem(_base.BaseItem, _base.ItemABC):
    """A DaemonSet in the Kubernetes cluster.

    A Daemon Set ensures that all (or some) nodes run a copy of a pod.

    :param cluster: The cluster this DaemonSet exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.DaemonSet
    resource = 'daemonsets'
    api_paths = API_PATHS

    @_util.statusproperty
    def current_number_scheduled(self):
        """The number of nodes that are running at least 1 daemon pod.

        The count is of those nodes that are running at least one daemon
        pod and that are supposed to run the daemon pod.
        """
        return self.raw['status']['currentNumberScheduled']

    @_util.statusproperty
    def number_misscheduled(self):
        """Number of nodes running the daemon pod, but not supposed to be."""
        return self.raw['status']['numberMisscheduled']

    @_util.statusproperty
    def desired_number_scheduled(self):
        """The total number of nodes that should be running the daemon pod.

        This includes nodes correctly running the daemon pod.
        """
        return self.raw['status']['desiredNumberScheduled']

    @_util.statusproperty
    def number_ready(self):
        """The number of nodes that have one or more of the daemon pod ready.

        Nodes counted are those that should be running the daemon pod and
        have one or more of the daemon pod running and ready.
        """
        return self.raw['status']['numberReady']

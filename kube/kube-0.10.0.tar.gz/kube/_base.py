"""Some base classes and ABCs for kube.

While all implementations are supposed to at least register their
classes, subclassing is not really an aim.  With the exception of
:meth:`__repr__`, most properties and methods are marked as abstract
and do not have a common implementation even if they could.  To share
code, instead, helper functions in ``kube._util`` should be used.
"""

import abc
import enum

import pyrsistent

from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class ViewABC(metaclass=abc.ABCMeta):         # pragma: nocover
    """Represents a view to a collection of resources.

    All top-level resources in Kubernetes have a collection, resources
    of a ``*List`` kind, with some common functionality.  This ABC
    defines views to provide access to resources in collections in a
    uniform way.  Note that a view is not the same as the collection
    resource, e.g. collections resources have some metadata associated
    with them and exist at a particular point in time, they have a
    metadata.resourceVersion, which views do not have.

    It is always possible to create an instance of this without
    needing to do any requests to the real Kubernetes cluster.

    :param cluster: The cluster this resource list is part of.
    :type cluster: kube.Cluster
    :param namespace: The optional namespace this resource list is
       part of.  If the resource list is not part of a namespace this
       will be ``None`` which means it will be a view to all resources
       of a certain type, regardless of their namespace.
    :type namespace: str

    :raises kube.NamespaceError: When a namespace is provided but the
       resource does not support one.
    """

    @abc.abstractmethod
    def __init__(self, cluster, namespace=None):
        pass

    @property
    @abc.abstractmethod
    def cluster(self):
        """The :class:`kube.Cluster` instance this resource is bound to."""

    @property
    @abc.abstractmethod
    def namespace(self):
        """The optional namespace this view is bound to.

        If the view is not bound to a namespace this will be ``None``,
        including for resources which do not support namespaces.
        """

    @abc.abstractmethod
    def __iter__(self):
        """Iterator of all resources in this collection.

        :raises kube.APIError: for errors from the k8s API server.
        """

    @property
    @abc.abstractmethod
    def kind(self):
        """The kind of the underlying Kubernetes resource.

        This is a :class:`kube.Kind` enum.

        This should be implemented as a static attribute since it
        needs to be available on the class as well as on the instance.
        """

    @property
    @abc.abstractmethod
    def resource(self):
        """The name of the Kubernetes API resource.

        The resource name is used in the construction of the API
        endpoint, e.g. for the API endpoint
        ``/namespaces/default/pods/`` the resource name is ``pods``.
        The resource name is identical for both the resource as well
        as the resource item, e.g. both objects with ``PodList`` and
        ``Pod`` as kind will have a resource name of ``pods``.

        This should be implemented as a static attribute since it
        needs to be available on the class as well as on the instance.
        """

    @property
    @abc.abstractmethod
    def api_paths(self):
        """The list of possible Kubernetes API version base paths for resource.

        This is a list of the API base path string for each of the
        existing API versions that could be used in the construction of the
        API endpoint for a resource, if available. For example,
        ``['api/v1', '/apis/extensions/v1beta1']``. They are listed in
        reverse chronological order, the most recent API version appearing
        first. kube uses the list to establish and use the most recent API
        version available.
        """

    @abc.abstractmethod
    def fetch(self, name, namespace=None):
        """Retrieve the current version of a single resource item by name.

        If the view itself is associated with a namespace,
        ``self.namespace is not None``, then this will default to
        fetching the resource item from this namespace.  If the view
        is not associated with a namespace, ``self.namespace is
        None``, and the resource requires a namespace then a
        :class:`kube.NamespaceError` is raised.  Note that the
        ``default`` namespace is not automatically used in this case.

        :param str name: The name of the resource.
        :param str namespace: The namespace to fetch the resource
           from.

        :returns: A single instance representing the resource.

        :raises LookupError: If the resource does not exist.
        :raises kube.NamespaceError: For an invalid namespace, either
           because the namespace is required for this resource but not
           provided or the resource does not support namespaces and
           one was provided.
        :raises kube.APIError: For errors from the k8s API server.
        """

    @abc.abstractmethod
    def filter(self, *, labels=None, fields=None):
        """Return an iterable of a subset of the resources.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: An iterator of :class:`kube.ItemABC` instances of
           the correct type for the resrouce which match the given
           selector.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: For errors from the k8s API server.
        """

    @abc.abstractmethod
    def watch(self):
        """Watch for changes to any of the resources in the view.

        Whenever one of the resources in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances.

        :raises kube.NamespaceError: Whe the namespace no longer
           exists.
        :raises kube.APIError: For errors from the k8s API server.
        """


class ItemABC(metaclass=abc.ABCMeta):  # pragma: nocover
    """Representation for a kubernetes resource.

    This is the interface all resource items must implement.

    :param cluster: The cluster this resource is bound to.
    :type cluster: kube.Cluster
    :param raw: The decoded JSON representing the resource.
    :type raw: dict
    """

    @abc.abstractmethod
    def __init__(self, cluster, raw):
        pass

    @property
    @abc.abstractmethod
    def cluster(self):
        """The :class:`kube.Cluster` instance this resource is bound to."""

    @property
    @abc.abstractmethod
    def raw(self):
        """The raw decoded JSON representing the resource.

        This behaves like a dict but is actually an immutable view of
        the dict.
        """

    @abc.abstractmethod
    def fetch(self):
        """Fetch the current version of the resource item.

        This will return a new instance of the current resource item
        at it's latest version.  This is useful to see any changes
        made to the object since it was last retrieved.

        :returns: An instance of the relevant :class:`ItemABC`
           subclass.

        :raises kube.APIError: For errors from the k8s API server.
        """
        data = self.cluster.proxy.get(self.meta.link)
        return self.__class__(self.cluster, data)

    @property
    @abc.abstractmethod
    def kind(self):
        """The Kubernetes resource kind of the resource.

        This is a :class:`kube.Kind` enum.

        This should be implemented as a static attribute since it
        needs to be available on the class as well as on the instance.
        """

    @property
    @abc.abstractmethod
    def resource(self):
        """The name of the Kubernetes API resource.

        The resource name is used in the construction of the API
        endpoint, e.g. for the API endpoint
        ``/namespaces/default/pods/`` the resource name is ``pods``.
        The resource name is identical for both the resource as well
        as the resource item, e.g. both objects with ``PodList`` and
        ``Pod`` as kind will have a resource name of ``pods``.

        This should be implemented as a static attribute since it
        needs to be available on the class as well as on the instance.
        """

    @property
    @abc.abstractmethod
    def api_paths(self):
        """The list of possible Kubernetes API version base paths for resource.

        This is a list of the API base path string for each of the
        existing API versions that could be used in the construction of the
        API endpoint for a resource, if available. For example,
        ``['api/v1', '/apis/extensions/v1beta1']``. They are listed in
        reverse chronological order, the most recent API version appearing
        first. kube uses the list to establish and use the most recent API
        version available.
        """

    @property
    @abc.abstractmethod
    def meta(self):
        """The resource's metadata as a :class:`kube.ObjectMeta` instance."""

    @abc.abstractmethod
    def spec(self):
        """The spec of this node's resource.

        This returns a copy of the raw, decoded JSON data
        representing the spec of this resource which can be used to
        re-create the resource.
        """

    @abc.abstractmethod
    def watch(self):
        """Watch the resource item for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvents` instances
           for the resource item.

        :raises kube.APIError: For errors from the k8s API server.
        """

    @abc.abstractmethod
    def delete(self):
        """Delete the resource item.

        :rtype: None

        :raises APIError: For errors from the k8s API server.
        """


class BaseView:
    """Optional base class to implement ViewABC.

    This base class provides a common implementation for some of the
    :class:`ViewABC` interface abstract methods.  Driving from this
    will not automatically make you an :class:`ItemABC` instance, you
    still need to either subclass or register the :class:`ItemABC` as
    well.

    Note the base-class is for resources which reside in a namespace.
    When using this as a base-class for resources which do not have a
    namespace some of the methods can not be used and will need to be
    overwritten.
    """
    # Subclasses must override these:
    kind = None
    resource = None
    api_paths = None
    _api_path = None

    def __init__(self, cluster, namespace=None):
        self._cluster = cluster
        self._namespace = namespace

    @property
    def cluster(self):
        """The cluster instance this view is bound to."""
        return self._cluster

    @property
    def namespace(self):
        """The optional namespace this view is bound to."""
        return self._namespace

    def _create_item(self, data):
        """Create an instance of the item.

        :param data: The raw data of the item.
        :type data: dict.
        """
        itemkind = Kind(self.kind.value[:-4])
        itemcls = self.cluster.kindimpl(itemkind)
        return itemcls(self.cluster, data)

    @property
    def api_path(self):
        """The most recent accessible k8s API base path string.

        For example, 'api/v1'.
        """
        if self._api_path:
            return self._api_path
        self._api_path = _util.find_api_path(
            self._cluster.proxy.base_url, self.api_paths, self.resource)
        return self._api_path

    def __iter__(self):
        """Iterator over all items in this view.

        :raise kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            path = [self.api_path, 'namespaces', self.namespace, self.resource]
        else:
            path = [self.api_path, self.resource]
        data = self.cluster.proxy.get(*path)
        for item in data['items']:
            yield self._create_item(item)

    def fetch(self, name, namespace=None):
        """Retrieve an individual resource item by name.

        This returns the current version of the resource item.

        :param str name: The name of the item to retrieve.
        :param str namespace: The namespace of the item to retrieve.

        :return: A single :class:`kube.NodeItem` instance.
        :raises LookupError: If the node does not exist.
        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.NamespaceError: If a namespace is used.
        """
        # Note: This method cannot be used by resources which do not
        #       have a namespace as this implementation requires a
        #       namespace.
        ns = namespace or self.namespace
        if not ns:
            raise _error.NamespaceError('Missing namespace')
        data = _util.fetch_resource(self.cluster, self.api_path,
                                    self.resource, name, namespace=ns)
        return self._create_item(data)

    def filter(self, *, labels=None, fields=None):
        """Return an iterable of a subset of the resources.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: An iterator of :class:`kube.ItemABC` instances
           of the correct type for the resrouce.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: for errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster,
                                      self.api_path, self.resource,
                                      labels=labels, fields=fields,
                                      namespace=self.namespace)
        for item in data_iter:
            yield self._create_item(item)

    def watch(self):
        """Watch the resource of this view for changes to items.

        Whenever one of the resources items in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be of
           the relevant :class:`kube.ItemABC` instance for the kind.

        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            path = [self.api_path, 'namespaces', self.namespace, self.resource]
        else:
            path = [self.api_path, self.resource]
        itemlist = self.cluster.proxy.get(*path)
        version = itemlist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch(*path, version=version)
        itemkind = Kind(self.kind.value[:-4])
        itemcls = self.cluster.kindimpl(itemkind)
        return _watch.ResourceWatcher(self.cluster, jsonwatcher, itemcls)

    def __repr__(self):
        if self.namespace is None:
            return '<{0.__class__.__name__}>'.format(self)
        else:
            return ('<{0.__class__.__name__} namespace={0.namespace}>'
                    .format(self))


class BaseItem:
    """Optional base class to implement ItemABC.

    This base class provides a common implementation for some of the
    :class:`ItemABC` interface abstract methods.  Deriving from this
    will not automatically make you an :class:`ItemABC` instance, you
    still need to either subclass or register the :class:`ItemABC` as
    well.
    """

    def __init__(self, cluster, raw):
        self._cluster = cluster
        self._raw = pyrsistent.freeze(raw)

    @property
    def cluster(self):
        """The :class:`kube.Cluster` instance this resource is bound to."""
        return self._cluster

    @property
    def raw(self):
        """The raw decoded JSON representing the resource."""
        return self._raw

    @property
    def meta(self):
        """The items' metadata as a :class:`kube.meta.ObjectMeta` instance.

        This provides access to the name, labels etc. of the resource item.
        """
        return _meta.ObjectMeta(self)

    def spec(self):
        """The spec of this resource item.

        This is the raw, decoded JSON data representing the spec of
        this resource item.
        """
        return pyrsistent.thaw(self.raw['spec'])

    def fetch(self):
        """Fetch the current version of the resource item.

        This will return a new instance of the current resource item
        at it's latest version.  This is useful to see any changes
        made to the object since it was last retrieved.

        :returns: An instance of the relevant :class:`ItemABC`
           subclass.

        :raises LookupError: If the resource item no longer exits.
        :raises kube.APIError: For errors from the k8s API server.
        """
        try:
            data = self.cluster.proxy.get(self.meta.link)
        except _error.APIError as err:
            if err.status_code == 404:
                raise LookupError from err
            else:
                raise
        return self.__class__(self.cluster, data)

    def watch(self):
        """Watch the resource item for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvents` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.NodeItem` instance.
        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)

    def delete(self):
        """Delete the resource item.

        If the item does not exist this will silently do nothing,
        following Kubernetes' principle of being a level-based system
        and the desired state is already present so all is fine.

        :rtype: None

        :raises APIError: For errors from the k8s API server.
        """
        try:
            print("self.meta.link:", self.meta.link)
            print(type(self.cluster.proxy))
            import traceback
            self.cluster.proxy.delete(self.meta.link)
        except _error.APIError as err:
            if err.status_code != 404:
                print("HERE NOT 404!", err.status_code, traceback.print_exc())
                raise

    def __repr__(self):
        if self.meta.namespace is not None:
            return ('<{0.__class__.__name__} {0.meta.name} '  # pylint: disable=missing-format-attribute
                    'namespace={0.meta.namespace}>' .format(self))
        else:
            return '<{0.__class__.__name__} {0.meta.name}>'.format(self)  # pylint: disable=missing-format-attribute


class Kind(enum.Enum):
    """The kinds of Kubernetes resources."""
    DaemonSet = 'DaemonSet'
    DaemonSetList = 'DaemonSetList'
    Deployment = 'Deployment'
    DeploymentList = 'DeploymentList'
    Node = 'Node'
    NodeList = 'NodeList'
    Namespace = 'Namespace'
    NamespaceList = 'NamespaceList'
    Pod = 'Pod'
    PodList = 'PodList'
    ReplicaSet = 'ReplicaSet'
    ReplicaSetList = 'ReplicaSetList'
    ReplicationController = 'ReplicationController'
    ReplicationControllerList = 'ReplicationControllerList'
    Service = 'Service'
    ServiceList = 'ServiceList'
    Secret = 'Secret'
    SecretList = 'SecretList'

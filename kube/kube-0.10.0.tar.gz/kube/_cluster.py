"""Tools to work with a Kubernetes cluster.

This module contains the top level tools to work with a Kubernetes
cluster and it's API server.
"""

import urllib.parse

import requests

from kube import _base
from kube import _daemonset
from kube import _deployment
from kube import _error
from kube import _namespace
from kube import _node
from kube import _pod
from kube import _replicaset
from kube import _replicationcontroller
from kube import _secret
from kube import _service
from kube import _util
from kube import _watch


# Kubernetes resources accessed via the API extensions.
API_EXTENSIONS = {'daemonsets', 'deployments', 'replicasets'}


class Cluster:
    """A Kubernetes cluster.

    The entry point to control a Kubernetes cluster.  There is only one
    connection mechanism, which is via a local API server proxy.  This
    is normally achieved by running ``kubectl proxy``.

    :param str url: The URL of the API server.
    """
    _CLS_MAP = {
        _base.Kind.DaemonSet: _daemonset.DaemonSetItem,
        _base.Kind.DaemonSetList: _daemonset.DaemonSetView,
        _base.Kind.Deployment: _deployment.DeploymentItem,
        _base.Kind.DeploymentList: _deployment.DeploymentView,
        _base.Kind.Node: _node.NodeItem,
        _base.Kind.NodeList: _node.NodeView,
        _base.Kind.Namespace: _namespace.NamespaceItem,
        _base.Kind.NamespaceList: _namespace.NamespaceView,
        _base.Kind.ReplicaSet: _replicaset.ReplicaSetItem,
        _base.Kind.ReplicaSetList: _replicaset.ReplicaSetView,
        _base.Kind.ReplicationController:
            _replicationcontroller.ReplicationControllerItem,
        _base.Kind.ReplicationControllerList:
            _replicationcontroller.ReplicationControllerView,
        _base.Kind.Pod: _pod.PodItem,
        _base.Kind.PodList: _pod.PodView,
        _base.Kind.Service: _service.ServiceItem,
        _base.Kind.ServiceList: _service.ServiceView,
        _base.Kind.Secret: _secret.SecretItem,
        _base.Kind.SecretList: _secret.SecretView,
    }

    def __init__(self, url='http://localhost:8001/'):
        if not url.endswith('/'):
            url += '/'
        self.api_base_url = url
        self.proxy = APIServerProxy(self.api_base_url)
        self.daemonsets = self.kindimpl(_base.Kind.DaemonSetList)(self)
        self.deployments = self.kindimpl(_base.Kind.DeploymentList)(self)
        self.nodes = self.kindimpl(_base.Kind.NodeList)(self)
        self.namespaces = self.kindimpl(_base.Kind.NamespaceList)(self)
        self.replicasets = self.kindimpl(_base.Kind.ReplicaSetList)(self)
        self.replicationcontrollers = self.kindimpl(
            _base.Kind.ReplicationControllerList)(self)
        self.pods = self.kindimpl(_base.Kind.PodList)(self)
        self.services = self.kindimpl(_base.Kind.ServiceList)(self)
        self.secrets = self.kindimpl(_base.Kind.SecretList)(self)

    def close(self):
        """Close and clean up underlying resources."""
        self.proxy.close()

    @classmethod
    def kindimpl(cls, kind):
        """Return the class which implements the resource kind.

        :param kind: The :class:`kube.Kind` instance.
        :type kind: kube.Kind

        :returns: A class implementing either :class:`kube.ViewABC` or
           :class:`kube.ItemABC` depending on the kind.

        :raises ValueError: If the kind is not known.
        """
        try:
            return cls._CLS_MAP[kind]
        except KeyError as err:
            raise ValueError('Unknown kind') from err

    def create(self, data, namespace=None):
        """Create a new resource item.

        :param data: The specification to create the resource from,
           this must include the ``apiVersion``, ``kind``,
           ``metadata`` and ``spec`` fields.  It is usually simply the
           de-serialised YAML but allows you to insert template
           processing if you require so.
        :type data: dict
        :param namespace: Create the resource item in the given
           namespace.  If the ``spec`` includes a namespace this
           namespace must match or an exception will be raised.
        :type namespace: str

        :returns: The newly created item.
        :rtype: A :class:`kube.ViewABC` instance of the right type
           according to the kind of resource item created based on the
           data in the spec.

        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.KubeError: If the spec is incomplete or the kind
           is unknown.
        """
        try:
            kind = data['kind']
        except KeyError as err:
            raise _error.KubeError('No resource kind found') from err
        try:
            kind = _base.Kind(kind)
        except ValueError as err:
            raise _error.KubeError('Unknown kind') from err
        item_cls = self.kindimpl(kind)
        api_path = _util.find_api_path(self.api_base_url,
                                       item_cls.api_paths,
                                       item_cls.resource)
        path = [api_path, item_cls.resource]
        if namespace is not None:
            path = [api_path, 'namespaces', namespace, item_cls.resource]
        new = self.proxy.post(*path, json=data)
        return item_cls(self, new)

    def __enter__(self):
        return self

    def __exit__(self, exc_val, exc_type, traceback):
        self.close()


class APIServerProxy:
    """Helper class to directly communicate with the API server.

    Since most classes need to communicate with the Kubernetes
    cluster's API server in a common way, this class helps take care of
    the common logic.  It also keeps the requests session alive to
    enable connection pooling to the API server.

    :param str base_url: The URL of the API, not including the API version.
    """
    def __init__(self, base_url='http://localhost:8001/'):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self._session = requests.Session()

    def close(self):
        """Close underlying connections.

        Once the proxy has been closed then the it can no longer be used
        to issue further requests.
        """
        self._session.close()

    def urljoin(self, *path):
        """Wrapper around urllib.parse.urljoin for the configured base URL.

        :param path: Individual relative path components, they will be
           joined using "/".  None of the path components should
           include a "/" separator themselves, other than the first
           component, the API path, which may.
        """
        return urllib.parse.urljoin(self.base_url, '/'.join(path))

    def get(self, *path, **params):
        """HTTP GET the path from the API server.

        :param str path: Individual API path components, they will
           be joined using "/".  None of the path components should
           include a "/" separator themselves, other than the first
           component, the API path, which may.
        :param dict params: Extra query parameters for the URL of the
           GET request as a dictionary of strings.

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        response = self._session.get(url, params=params)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to GET {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def post(self, *path, json=None, **params):
        """HTTP POST to the relative path on the API server.

        :param path: Individual relative path components, they will be
           joined using :meth:`urljoin`.
        :type path: str
        :param json: The body to post, which will be JSON-encoded
           before posting.
        :type json: collections.abc.Mapping
        :param params: Extra query parameters for the URL of the POST
           request.
        :type params: str

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 201
           Created.
        """
        url = self.urljoin(*path)
        response = self._session.post(url, json=json, params=params)
        if response.status_code != 201:
            raise _error.APIError(response, 'Failed to POST {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def delete(self, *path, json=None, **params):
        """HTTP DELETE to the relative path on the API server.

        :param path: Individual relative path components, they will be
           joined using :meth:`urljoin`.
        :type path: str
        :param json: The body, which will be JSON-encoded before
           posting.
        :type json: collections.abc.Mapping
        :param params: Extra query parameters for the URL of the
           DELETE request.
        :type params: str

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        response = self._session.delete(url, json=json, params=params)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to DELETE {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def patch(self, *path, patch=None):
        """HTTP PATCH as application/strategic-merge-patch+json.

        This allows using the Strategic Merge Patch to patch a
        resource on the Kubernetes API server.

        :param str path: Individual relative path components, they
           will be joined using "/".  None of the path components
           should include a "/" separator themselves, other than the first
           component, the API path, which may - unless you only
           provide one component, which will be joined to the base URL
           using :func:`urllib.parse.urljoin`.  This case can be
           useful to use the links provided by the API itself
           directly, e.g. from a resource's ``metadata.selfLink``
           field.
        :param dict patch: The decoded JSON object with the patch
           data.

        :returns: The decoded JSON object of the resource after
           applying the patch.

        :raises APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        headers = {'Content-Type': 'application/strategic-merge-patch+json'}
        response = self._session.patch(url, headers=headers, json=patch)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to PATCH {}:'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def watch(self, *path, version=None, fields=None):
        """Watch a list resource for events.

        This issues a request to the API with the ``watch`` query
        string parameter set to ``true`` which returns a chunked
        response.  An iterator is returned which continuously reads
        from the response, yielding received lines as bytes.

        :param path: The URL path to the resource to watch. See
            :meth:`urljoin`.
        :param str version: The resource version to start watching from.
        :param dict fields: A dict of fields which must match their
           values.  This is a limited form of the full fieldSelector
           format, it is limited because filtering is done at client
           side for consistency.

        :returns: An special iterator which allows non-blocking
           iterating using a ``.next(timeout)`` method.  Using it as a
           normal iterator will result in blocking behaviour.
        :rtype: :class:`kube._watch.JSONWatcher`.

        :raises APIError: If there is a problem with the API server.
        """
        return _watch.JSONWatcher(self, *path, version=version, fields=fields)

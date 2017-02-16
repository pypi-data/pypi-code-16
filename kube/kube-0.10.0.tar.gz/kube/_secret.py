"""Interface for Secret resources."""

import base64
import enum

from kube import _base


API_PATHS = ['api/v1']


class SecretView(_base.BaseView, _base.ViewABC):
    """View of the Secret resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    """
    kind = _base.Kind.SecretList
    resource = 'secrets'
    api_paths = API_PATHS


class SecretType(enum.Enum):
    """Enumeration of secret types."""
    Opaque = 'Opaque'


class SecretItem(_base.BaseItem, _base.ItemABC):
    """A Secret in the Kubernetes cluster.

    :param cluster: The cluster this Service exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar kind: The kind of the underlying Kubernetes resource item.
    :cvar resource: The name of the Kubernetes API resource.
    :cvar SecretType: Shortcut to :class:`kube.SecretType`.
    """
    kind = _base.Kind.Secret
    resource = 'secrets'
    api_paths = API_PATHS
    SecretType = SecretType

    def spec(self):
        """An empty dictionary.

        This is supposed to be the secret resource item's spec.  But
        secrets do not have a spec, so to still follow the
        :class:`kube.ItemABC` we return an empty dict.
        """
        return {}

    @property
    def type(self):
        """The type of secret.

        There currently is only the "Opaque" type.
        """
        return self.SecretType(self.raw['type'])

    @property
    def data(self):
        """A mapping of the secret data.

        A copy of the secret data as a dict.  The keys are the names
        of the secrets as a (unicode) string, while the values are the
        secrets as bytestrings.

        Secret values are stored in a base64 encoding on the k8s
        master, but this is an implementation detail that this
        property takes care off for you.
        """
        data = {}
        for name, value in self.raw.get('data', {}).items():
            data[name] = base64.b64decode(value)
        return data

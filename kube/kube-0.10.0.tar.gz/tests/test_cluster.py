import time
import unittest.mock

import requests
import pytest

import kube
from kube import _base
from kube import _cluster
from kube import _daemonset
from kube import _error
from kube import _testing
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def api_path_mock(monkeypatch):
    mockpath = unittest.mock.Mock(return_value='api/v1')
    monkeypatch.setattr(_util, 'find_api_path', mockpath)
    return mockpath


class TestCluster:

    def test_init_url(self):
        c = _cluster.Cluster(url='http://localhost:8001/')
        assert c.proxy.base_url == 'http://localhost:8001/'

    def test_proxy(self, cluster):
        assert isinstance(
            cluster.proxy,
            (_cluster.APIServerProxy, _testing.StubAPIServerProxy),
        )

    def test_views(self, cluster):
        assert isinstance(cluster.namespaces, kube.NamespaceView)
        assert isinstance(cluster.nodes, kube.NodeView)
        assert isinstance(cluster.pods, kube.PodView)
        assert isinstance(cluster.replicasets, kube.ReplicaSetView)
        assert isinstance(cluster.services, kube.ServiceView)
        assert isinstance(cluster.secrets, kube.SecretView)

    def test_kindimpl(self, cluster):
        assert cluster.kindimpl(kube.Kind.Namespace) is kube.NamespaceItem
        assert cluster.kindimpl(kube.Kind.NamespaceList) is kube.NamespaceView
        with pytest.raises(ValueError):
            cluster.kindimpl(None)

    def test_close(self):
        cluster = kube.Cluster()
        orig_proxy_close = cluster.proxy.close
        closed = False
        def close():
            nonlocal closed
            closed = True
            orig_proxy_close()
        cluster.proxy.close = close
        cluster.close()
        assert closed

    def test_context_manager(self):
        closed = False
        with kube.Cluster() as cluster:
            orig_proxy_close = cluster.proxy.close
            def close():
                nonlocal closed
                closed = True
                orig_proxy_close()
            cluster.proxy.close = close
        assert closed

    def test_create(self, request, cluster):
        data = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'generateName': 'testns-',
            },
        }
        item = cluster.create(data)
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces', item.meta.name)
        request.addfinalizer(fin)
        assert isinstance(item, _base.ItemABC)
        assert item.kind is _base.Kind.Namespace

    def test_create_with_ns(self, request, cluster):
        data = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'generateName': 'testsecret-',
            },
        }
        item = cluster.create(data, namespace='default')
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces',
                                 'default', 'secrets', item.meta.name)
        request.addfinalizer(fin)
        assert isinstance(item, _base.ItemABC)
        assert item.kind is _base.Kind.Secret

    def test_create_nokind(self, cluster):
        data = {
            'apiVersion': 'v1',
            'metadata': {
                'generateName': 'testkind-',
            },
        }
        with pytest.raises(_error.KubeError):
            cluster.create(data)

    def test_create_badkind(self, cluster):
        data = {
            'apiVersion': 'v1',
            'kind': 'ThisKindDoesNotExist',
            'metadata': {
                'generateName': 'testkind-',
            },
        }
        with pytest.raises(_error.KubeError):
            cluster.create(data)

    def test_api_path_call(self, cluster, api_path_mock):
        list(_daemonset.DaemonSetView(cluster))
        api_path_mock.assert_called_with(
            'http://localhost:8001/',
            ['apis/extensions/v1beta1'], 'daemonsets')


class FakeResponse:
    """A primitive stubbing of requests.Response."""

    def __init__(self, status, data):
        self.status_code = status
        self.data = data

    def json(self, cls=None):   # pylint: disable=unused-argument
        return self.data


class FakeSession:
    """A primitive stubbing of requests.Session.

    We could probably do something more advanced like using betamax or
    even just mock.  But that would introduce extra dependencies and
    the use for them is not that great yet.
    """

    def __init__(self):
        self.closed = False
        self._stub_proxy = _testing.StubAPIServerProxy()

    def close(self):
        self.closed = True

    def get(self, url, params=None):
        try:
            data = self._stub_proxy.get(url, params=params)
        except _error.APIError as err:
            data = {'status_code': err.status_code, 'message': str(err)}
            return FakeResponse(err.status_code, data)
        else:
            return FakeResponse(200, data)

    def post(self, url, json=None, params=None):
        try:
            data = self._stub_proxy.post(url, json=json, params=params)
        except _error.APIError as err:
            data = {'status_code': err.status_code, 'message': str(err)}
            return FakeResponse(err.status_code, data)
        else:
            return FakeResponse(201, data)

    def delete(self, url, json=None, params=None):
        try:
            data = self._stub_proxy.delete(url, json=json, params=params)
        except _error.APIError as err:
            data = {'status_code': err.status_code, 'message': str(err)}
            return FakeResponse(err.status_code, data)
        else:
            return FakeResponse(200, data)

    def patch(self, url, headers=None, json=None):  # pylint: disable=unused-argument
        try:
            data = self._stub_proxy.patch(url, patch=json)
        except _error.APIError as err:
            data = {'status_code': err.status_code, 'message': str(err)}
            return FakeResponse(err.status_code, data)
        else:
            return FakeResponse(200, data)


class TestAPIServerProxy:

    @pytest.fixture
    def proxy(self, request, monkeypatch):
        if not request.config.getoption('verify'):
            monkeypatch.setattr(requests, 'Session', FakeSession)
        return _cluster.APIServerProxy()

    def test_init_url(self):
        p0 = _cluster.APIServerProxy()
        p1 = _cluster.APIServerProxy(base_url='http://localhost:8001/')
        assert p1.base_url.endswith('/')
        assert p1.base_url == p0.base_url

    def test_close(self, proxy):
        orig_close = proxy._session.close
        closed = False
        def close():
            nonlocal closed
            closed = True
            orig_close()
        proxy._session.close = close
        proxy.close()
        assert closed

    def test_urljoin(self, proxy):
        url = proxy.urljoin('api/v1', 'namespaces', 'default')
        assert url == 'http://localhost:8001/api/v1/namespaces/default'

    def test_get_200(self, proxy):
        ret = proxy.get('api/v1', 'namespaces', 'default')
        assert ret['metadata']['name'] == 'default'

    def test_get_404(self, proxy):
        with pytest.raises(kube.APIError):
            proxy.get('api/v1', 'this-resource-does-not-exist', 'foo')

    def test_post_201(self, request, proxy):
        data = {
            'metadata': {
                'generateName': 'testns-',
            },
        }
        ret = proxy.post('api/v1', 'namespaces', json=data)
        name = ret['metadata']['name']
        def fin():
            proxy.delete('api/v1', 'namespaces', name)
        request.addfinalizer(fin)
        assert name.startswith('testns-')

    def test_post_404(self, proxy):
        with pytest.raises(kube.APIError):
            proxy.post('api/v1', 'this-resource-does-not-exist')

    def test_delete_200(self, proxy):
        data = {
            'metadata': {
                'generateName': 'testns-',
            },
        }
        ret = proxy.post('api/v1', 'namespaces', json=data)
        name = ret['metadata']['name']
        proxy.delete('api/v1', 'namespaces', name)
        with pytest.raises(kube.APIError):
            # Real clusters take a little while to delete the namespace
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                proxy.get('api/v1', 'namespaces', name)

    def test_delete_404(self, proxy):
        with pytest.raises(kube.APIError):
            proxy.delete('api/v1', 'this-resource-does-not-exist', 'foo')

    def test_patch_200(self, request, proxy):
        ns = proxy.get('api/v1', 'namespaces', 'default')
        assert 'test/patch' not in ns['metadata'].get('labels', {})
        patch = {'metadata': {'labels': {'test/patch': 'val'}}}
        ret = proxy.patch('api/v1', 'namespaces', 'default', patch=patch)
        def fin():
            patch = {'metadata': {'labels': {'test/patch': None}}}
            proxy.patch('api/v1', 'namespaces', 'default', patch=patch)
        request.addfinalizer(fin)
        assert 'test/patch' in ret['metadata']['labels']

    def test_patch_404(self, proxy):
        with pytest.raises(kube.APIError):
            proxy.patch(
                'api/v1', 'this-resource-does-not-exist', 'foo', patch={})

    def test_watch(self, proxy, monkeypatch):
        def watcher(self, *path, version=None, fields=None):  # pylint: disable=unused-argument
            return path, version, fields
        monkeypatch.setattr(_watch, 'JSONWatcher', watcher)
        version = object()
        fields = object()
        ret = proxy.watch('api/v1', 'namespaces',
                          'default', version=version, fields=fields)
        assert ret == (('api/v1', 'namespaces', 'default'), version, fields)

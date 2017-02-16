import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch

from kube import _secret


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


@pytest.fixture(scope='module')
def testsec(request, cluster):
    """A test secret which exists in the cluster."""
    data = {
        'apiVersion': 'v1',
        'kind': 'Secret',
        'metadata': {
            'generateName': 'testsec-',
            'labels': {
                'test/sec': 'testsec',
            },
            'namespace': 'default',
        },
        'type': 'Opaque',
        'data': {
            'username': 'bXl1c2Vy',      # myuser
            'password': 'bXlzZWNyZXQ=',  # mysecret
        },
    }
    ret = cluster.proxy.post('api/v1', 'namespaces',
                             'default', 'secrets', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'secrets', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestServiceView:

    @pytest.fixture
    def view(self, cluster):
        """A ServiceView instance."""
        return _secret.SecretView(cluster)

    def test_serviceview(self, view):
        assert isinstance(view, _base.ViewABC)
        assert view.namespace is None

    def test_create_namespace(self, cluster):
        view = _secret.SecretView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, view):
        assert view.kind is _base.Kind.SecretList

    @pytest.mark.parametrize('ns', [None, 'testsec'])
    def test_iter_type(self, cluster, testsec, ns):  # pylint: disable=unused-argument
        if ns == 'testsec':
            ns = testsec['metadata']['namespace']
        view = _secret.SecretView(cluster, namespace=ns)
        uids = []
        for svc in view:
            assert isinstance(svc, _secret.SecretItem)
            assert svc.meta.uid not in uids
            uids.append(svc.meta.uid)
        assert uids

    def test_fetch(self, view, testsec):
        name = testsec['metadata']['name']
        sec = view.fetch(name, namespace=testsec['metadata']['namespace'])
        assert isinstance(sec, _base.ItemABC)
        assert sec.meta.name == name

    def test_fetch_no_ns(self, view, testsec):
        with pytest.raises(_error.NamespaceError):
            view.fetch(testsec['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, testsec):
        view = _secret.SecretView(cluster,
                                  namespace=testsec['metadata']['namespace'])
        sec = view.fetch(testsec['metadata']['name'])
        assert isinstance(sec, _base.ItemABC)
        assert sec.meta.uid == testsec['metadata']['uid']

    def test_fetch_no_item(self, view):
        with pytest.raises(LookupError):
            view.fetch('this-secret-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize('filt', [{'test/sec': 'testsec'},
                                      'test/sec=testsec'])
    def test_filter_labels(self, view, testsec, filt):
        items = view.filter(labels=filt)
        assert testsec['metadata']['uid'] in {sec.meta.uid for sec in items}

    # @pytest.mark.xfail(reason='Seems unsupported for services')
    def test_filter_fields_dict(self, view, testsec):
        fields = {'metadata.name': testsec['metadata']['name']}
        items = list(view.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == testsec['metadata']['uid']

    # @pytest.mark.xfail(reason='Seems unsupported for services')
    def test_filter_fields_str(self, view, testsec):
        fields = 'metadata.name={sec.metadata.name}'.format(sec=testsec)
        items = list(view.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == testsec['metadata']['uid']

    def test_filter_ns(self, cluster, testsec):
        view = _secret.SecretView(cluster, namespace='default')
        secrets = [s.meta.name for s in view.filter()]
        assert testsec['metadata']['name'] in secrets

    @pytest.mark.parametrize('ns', [None, 'testsec'])
    def test_watch(self, request, cluster, testsec, ns):
        # pylint: disable=too-many-branches
        if ns == 'testsec':
            ns = testsec['metadata']['namespace']
        view = _secret.SecretView(cluster, namespace=ns)
        sec = view.fetch(testsec['metadata']['name'],
                         namespace=testsec['metadata']['namespace'])
        assert 'test/foo' not in sec.meta.labels
        request.addfinalizer(lambda: sec.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            sec.meta.labels.set('test/foo', 'val')
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    update = watcher.next(timeout=0.2)
                except TimeoutError:
                    continue
                except StopIteration:
                    pytest.fail('Watch iterator exhausted')
                else:
                    if 'test/foo' in update.item.meta.labels:
                        break
            else:
                pytest.fail('New labels not found')
        assert isinstance(update, _watch.WatchEvent)
        assert isinstance(update.evtype, _watch.WatchEventType)
        assert isinstance(update.item, _secret.SecretItem)


class TestSecretItem:

    @pytest.fixture
    def sec(self, cluster, testsec):
        """A test SecretItem instance."""
        return cluster.secrets.fetch(
            testsec['metadata']['name'],
            namespace=testsec['metadata']['namespace'])

    def test_secret(self, cluster, sec):
        assert sec.cluster is cluster

    def test_kind(self, sec):
        assert sec.kind is _base.Kind.Secret

    def test_raw(self, sec):
        assert isinstance(sec.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            sec.raw['foo'] = 'bar'

    def test_fetch(self, sec):
        sec1 = sec.fetch()
        assert sec != sec1
        assert sec.meta.uid == sec1.meta.uid

    def test_meta(self, sec):
        assert isinstance(sec.meta, _meta.ObjectMeta)

    def test_spec(self, sec):
        spec = sec.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in sec.spec()

    def test_watch(self, sec):
        assert 'test/watch' not in sec.meta.labels
        with sec.watch() as watcher:
            sec.meta.labels.set('test/watch', 'val')
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    update = watcher.next(timeout=0.2)
                except TimeoutError:
                    continue
                except StopIteration:
                    pytest.fail('Watch iterator exhausted')
                else:
                    if 'test/watch' in update.item.meta.labels:
                        break
            else:
                pytest.fail('New label not found')
        assert isinstance(update, _watch.WatchEvent)
        assert isinstance(update.evtype, _watch.WatchEventType)
        assert isinstance(update.item, _secret.SecretItem)

    def test_type(self, sec):
        assert sec.type is sec.SecretType.Opaque

    def test_data(self, sec):
        assert sec.data == {'username': b'myuser', 'password': b'mysecret'}

    @pytest.fixture(scope='module')
    def minimal_sec(self, request, cluster):
        """A test secret with minimal data."""
        data = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'generateName': 'testsec-',
                'namespace': 'default',
            },
        }
        ret = cluster.proxy.post('api/v1', 'namespaces',
                                 'default', 'secrets', json=data)
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces', 'default',
                                 'secrets', ret['metadata']['name'])
        request.addfinalizer(fin)
        return _secret.SecretItem(cluster, ret)

    def test_minimal_type(self, minimal_sec):
        assert minimal_sec.type is minimal_sec.SecretType.Opaque

    def test_minimal_data(self, minimal_sec):
        assert minimal_sec.data == {}

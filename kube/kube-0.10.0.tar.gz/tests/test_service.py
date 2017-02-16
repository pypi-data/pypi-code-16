import collections
import ipaddress
import time

import pyrsistent
import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch

from kube import _service


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


@pytest.fixture(scope='module')
def testsvc(request, cluster):
    """A service which exists in the cluster."""
    data = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'generateName': 'testsvc-',
            'labels': {
                'test/svc': 'testsvc',
            },
            'namespace': 'default',
        },
        'spec': {
            'selector': {
                'test/svc': 'testsvc',
            },
            'ports': [
                {
                    'protocol': 'TCP',
                    'port': 1234,
                    'targetPort': 4321,
                },
            ],
            'type': 'ClusterIP',
        },
    }
    ret = cluster.proxy.post('api/v1', 'namespaces',
                             'default', 'services', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'services', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestServiceView:

    @pytest.fixture
    def view(self, cluster):
        """A ServiceView instance."""
        return _service.ServiceView(cluster)

    def test_serviceview(self, view):
        assert isinstance(view, _base.ViewABC)
        assert view.namespace is None

    def test_create_namespace(self, cluster):
        view = _service.ServiceView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, view):
        assert view.kind is _base.Kind.ServiceList

    @pytest.mark.parametrize('ns', [None, 'testsvc'])
    def test_iter_type(self, cluster, testsvc, ns):  # pylint: disable=unused-argument
        if ns == 'testsvc':
            ns = testsvc['metadata']['namespace']
        view = _service.ServiceView(cluster, namespace=ns)
        uids = []
        for svc in view:
            assert isinstance(svc, _service.ServiceItem)
            assert svc.meta.uid not in uids
            uids.append(svc.meta.uid)
        assert uids

    def test_fetch(self, view, testsvc):
        name = testsvc['metadata']['name']
        svc = view.fetch(name, namespace=testsvc['metadata']['namespace'])
        assert isinstance(svc, _base.ItemABC)
        assert svc.meta.name == name

    def test_eftch_no_ns(self, view, testsvc):
        with pytest.raises(_error.NamespaceError):
            view.fetch(testsvc['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, testsvc):
        view = _service.ServiceView(cluster,
                                    namespace=testsvc['metadata']['namespace'])
        svc = view.fetch(testsvc['metadata']['name'])
        assert isinstance(svc, _base.ItemABC)
        assert svc.meta.uid == testsvc['metadata']['uid']

    def test_fetch_no_item(self, view):
        with pytest.raises(LookupError):
            view.fetch('this-svc-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize('filt', [{'test/svc': 'testsvc'},
                                      'test/svc=testsvc'])
    def test_filter_labels(self, view, testsvc, filt):
        items = view.filter(labels=filt)
        assert testsvc['metadata']['uid'] in {svc.meta.uid for svc in items}

    @pytest.mark.xfail(reason='Seems unsupported for services')
    def test_filter_fields_dict(self, view, testsvc):
        fields = {'metadata.name': testsvc['metadata']['name']}
        items = list(view.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == testsvc['metadata']['uid']

    @pytest.mark.xfail(reason='Seems unsupported for services')
    def test_filter_fields_str(self, view, testsvc):
        fields = 'metadata.name={svc.metadata.name}'.format(svc=testsvc)
        items = list(view.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == testsvc['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'testsvc'])
    def test_watch(self, request, cluster, testsvc, ns):   # pylint: disable=too-many-branches
        if ns == 'testsvc':
            ns = testsvc['metadata']['namespace']
        view = _service.ServiceView(cluster, namespace=ns)
        svc = view.fetch(testsvc['metadata']['name'],
                         namespace=testsvc['metadata']['namespace'])
        assert 'test/foo' not in svc.meta.labels
        request.addfinalizer(lambda: svc.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            svc.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _service.ServiceItem)


class TestServiceItem:

    @pytest.fixture
    def svc(self, cluster, testsvc):
        """A test ServiceItem instance."""
        return cluster.services.fetch(
            testsvc['metadata']['name'],
            namespace=testsvc['metadata']['namespace'])

    def test_service(self, cluster, svc):
        assert svc.cluster is cluster

    def test_kind(self, svc):
        assert svc.kind is _base.Kind.Service

    def test_raw(self, svc):
        assert isinstance(svc.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            svc.raw['foo'] = 'bar'

    def test_fetch(self, svc):
        svc1 = svc.fetch()
        assert svc != svc1
        assert svc.meta.uid == svc1.meta.uid

    def test_meta(self, svc):
        assert isinstance(svc.meta, _meta.ObjectMeta)

    def test_spec(self, svc):
        spec = svc.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in svc.spec()

    def test_watch(self, svc):
        assert 'test/watch' not in svc.meta.labels
        with svc.watch() as watcher:
            svc.meta.labels.set('test/watch', 'val')
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
        assert isinstance(update.item, _service.ServiceItem)

    @pytest.mark.parametrize('ingress', [{'ip': '192.0.2.1'},
                                         {'hostname': 'host.example.com'},
                                         {}])
    def test_loadbalancer_ingress(self, cluster, testsvc, ingress):
        data = pyrsistent.thaw(testsvc)
        data['status'] = {'loadBalancer': {'ingress': [ingress]}}
        svc = _service.ServiceItem(cluster, data)
        if 'ip' in ingress:
            addr = ipaddress.IPv4Address('192.0.2.1')
            assert svc.loadbalancer_ingress == {addr}
        elif 'hostname' in ingress:
            assert svc.loadbalancer_ingress == {'host.example.com'}
        else:
            with pytest.raises(_error.StatusError):
                assert svc.loadbalancer_ingress

    def test_loadbalancer_no_ingress(self, svc):
        with pytest.raises(_error.StatusError):
            assert svc.loadbalancer_ingress

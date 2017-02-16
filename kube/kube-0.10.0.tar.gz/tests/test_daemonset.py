import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _daemonset
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


@pytest.fixture(scope='module')
def pause(request, cluster):
    """A daemon set running the pause container."""
    data = {
        'apiVersion': 'v1',
        'kind': 'DaemonSet',
        'metadata': {
            'generateName': 'test-pause-',
            'labels': {
                'test/ds': 'pause',
            },
            'namespace': 'default',
        },
        'spec': {
            'selector': {
                'matchLabels': {
                    'test/ds': 'pause',
                },
            },
            'template': {
                'metadata': {
                    'labels': {
                        'test/ds': 'pause',
                    },
                    'namespace': 'default',
                },
                'spec': {
                    'containers': [
                        {
                            'name': 'pause',
                            'image': 'kubernetes/pause',
                        },
                    ],
                },
            },
        },
    }
    ret = cluster.proxy.post('api/v1', 'namespaces',
                             'default', 'daemonsets', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'daemonsets', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestDaemonSetView:

    @pytest.fixture
    def dsview(self, cluster):
        """A DaemonSetView instance."""
        return _daemonset.DaemonSetView(cluster)

    def test_daemonsetview(self, dsview):
        assert isinstance(dsview, _base.ViewABC)
        assert dsview.namespace is None

    def test_create_namespace(self, cluster):
        view = _daemonset.DaemonSetView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, dsview):
        assert dsview.kind is _base.Kind.DaemonSetList

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_iter_type(self, cluster, pause, ns):  # pylint: disable=unused-argument
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _daemonset.DaemonSetView(cluster, namespace=ns)
        uids = []
        for ds in view:
            assert isinstance(ds, _daemonset.DaemonSetItem)
            assert ds.meta.uid not in uids
            uids.append(ds.meta.uid)
        assert uids

    def test_fetch(self, dsview, pause):
        name = pause['metadata']['name']
        ds = dsview.fetch(name, namespace='default')
        assert isinstance(ds, _base.ItemABC)
        assert ds.meta.name == name

    def test_fetch_no_ns(self, dsview, pause):
        with pytest.raises(_error.NamespaceError):
            dsview.fetch(pause['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, pause):
        view = _daemonset.DaemonSetView(
            cluster, namespace=pause['metadata']['namespace'])
        ds = view.fetch(pause['metadata']['name'])
        assert isinstance(ds, _base.ItemABC)
        assert ds.meta.uid == pause['metadata']['uid']

    def test_fetch_no_item(self, dsview):
        with pytest.raises(LookupError):
            dsview.fetch('this-ds-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize('filt', [{'test/ds': 'pause'}, 'test/ds=pause'])
    def test_filter_labels(self, dsview, pause, filt):
        items = dsview.filter(labels=filt)
        assert pause['metadata']['uid'] in {ds.meta.uid for ds in items}

    def test_filter_fields_dict(self, dsview, pause):
        fields = {'metadata.name': pause['metadata']['name']}
        items = list(dsview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    def test_filter_fields_str(self, dsview, pause):
        fields = 'metadata.name={pause.metadata.name}'.format(pause=pause)
        items = list(dsview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_watch(self, request, cluster, pause, ns):    # pylint: disable=too-many-branches
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _daemonset.DaemonSetView(cluster, namespace=ns)
        ds = view.fetch(pause['metadata']['name'],
                        namespace=pause['metadata']['namespace'])
        assert 'test/foo' not in ds.meta.labels
        request.addfinalizer(lambda: ds.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            ds.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _daemonset.DaemonSetItem)


class TestDaemonSetItem:

    @pytest.fixture
    def ds(self, cluster, pause):
        """The pause DaemonSet."""
        return cluster.daemonsets.fetch(
            pause['metadata']['name'],
            namespace=pause['metadata']['namespace'])

    def test_daemonset(self, cluster, ds):
        assert ds.cluster is cluster

    def test_kind(self, ds):
        assert ds.kind is _base.Kind.DaemonSet

    def test_raw(self, ds):
        assert isinstance(ds.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            ds.raw['foo'] = 'bar'

    def test_fetch(self, ds):
        ds1 = ds.fetch()
        assert ds != ds1
        assert ds.meta.uid == ds1.meta.uid

    def test_meta(self, ds):
        assert isinstance(ds.meta, _meta.ObjectMeta)

    def test_spec(self, ds):
        spec = ds.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in ds.spec()

    def test_watch(self, ds):
        assert 'test/watch' not in ds.meta.labels
        with ds.watch() as watcher:
            ds.meta.labels.set('test/watch', 'val')
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
        assert isinstance(update.item, _daemonset.DaemonSetItem)

    def test_current_number_scheduled(self, ds):
        assert ds.current_number_scheduled == \
               ds.raw['status']['currentNumberScheduled']

    def test_number_misscheduled(self, ds):
        assert ds.number_misscheduled == ds.raw['status']['numberMisscheduled']

    def test_desired_number_scheduled(self, ds):
        assert ds.desired_number_scheduled == \
               ds.raw['status']['desiredNumberScheduled']

    def test_number_ready(self, ds):
        assert ds.number_ready == ds.raw['status']['numberReady']

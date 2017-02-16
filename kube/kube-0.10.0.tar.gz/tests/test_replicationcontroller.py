import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _replicationcontroller
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


@pytest.fixture(scope='module')
def pause(request, cluster):
    """A replicationcontroller running the pause container."""
    data = {
        'apiVersion': 'v1',
        'kind': 'ReplicationController',
        'metadata': {
            'generateName': 'test-pause-',
            'labels': {
                'test/rc': 'pause',
            },
            'namespace': 'default',
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'test/rc': 'pause',
                },
            },
            'template': {
                'metadata': {
                    'labels': {
                        'test/rc': 'pause',
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
    ret = cluster.proxy.post('api/v1', 'namespaces', 'default',
                             'replicationcontrollers', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'replicationcontrollers', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestReplicationControllerView:

    @pytest.fixture
    def rcview(self, cluster):
        """A ReplicationControllerView instance."""
        return _replicationcontroller.ReplicationControllerView(cluster)

    def test_replicationcontrollerview(self, rcview):
        assert isinstance(rcview, _base.ViewABC)
        assert rcview.namespace is None

    def test_create_namespace(self, cluster):
        view = _replicationcontroller.ReplicationControllerView(
            cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, rcview):
        assert rcview.kind is _base.Kind.ReplicationControllerList

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_iter_type(self, cluster, pause, ns):  # pylint: disable=unused-argument
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _replicationcontroller.ReplicationControllerView(
            cluster, namespace=ns)
        uids = []
        for rc in view:
            assert isinstance(
                rc, _replicationcontroller.ReplicationControllerItem)
            assert rc.meta.uid not in uids
            uids.append(rc.meta.uid)
        assert uids

    def test_fetch(self, rcview, pause):
        name = pause['metadata']['name']
        rc = rcview.fetch(name, namespace='default')
        assert isinstance(rc, _base.ItemABC)
        assert rc.meta.name == name

    def test_fetch_no_ns(self, rcview, pause):
        with pytest.raises(_error.NamespaceError):
            rcview.fetch(pause['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, pause):
        view = _replicationcontroller.ReplicationControllerView(
            cluster, namespace=pause['metadata']['namespace'])
        rc = view.fetch(pause['metadata']['name'])
        assert isinstance(rc, _base.ItemABC)
        assert rc.meta.uid == pause['metadata']['uid']

    def test_fetch_no_item(self, rcview):
        with pytest.raises(LookupError):
            rcview.fetch('this-rc-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize('filt', [{'test/rc': 'pause'}, 'test/rc=pause'])
    def test_filter_labels(self, rcview, pause, filt):
        items = rcview.filter(labels=filt)
        assert pause['metadata']['uid'] in {rc.meta.uid for rc in items}

    def test_filter_fields_dict(self, rcview, pause):
        fields = {'metadata.name': pause['metadata']['name']}
        items = list(rcview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    def test_filter_fields_str(self, rcview, pause):
        fields = 'metadata.name={pause.metadata.name}'.format(pause=pause)
        items = list(rcview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_watch(self, request, cluster, pause, ns):    #  pylint: disable=too-many-branches
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _replicationcontroller.ReplicationControllerView(
            cluster, namespace=ns)
        rc = view.fetch(pause['metadata']['name'],
                        namespace=pause['metadata']['namespace'])
        assert 'test/foo' not in rc.meta.labels
        request.addfinalizer(lambda: rc.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            rc.meta.labels.set('test/foo', 'val')
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
        assert isinstance(
            update.item, _replicationcontroller.ReplicationControllerItem)


class TestReplicationControllerItem:

    @pytest.fixture
    def rc(self, cluster, pause):
        """The pause ReplicationController."""
        return cluster.replicationcontrollers.fetch(
            pause['metadata']['name'],
            namespace=pause['metadata']['namespace'])

    def test_replicationcontroller(self, cluster, rc):
        assert rc.cluster is cluster

    def test_kind(self, rc):
        assert rc.kind is _base.Kind.ReplicationController

    def test_raw(self, rc):
        assert isinstance(rc.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            rc.raw['foo'] = 'bar'

    def test_fetch(self, rc):
        rc1 = rc.fetch()
        assert rc != rc1
        assert rc.meta.uid == rc1.meta.uid

    def test_meta(self, rc):
        assert isinstance(rc.meta, _meta.ObjectMeta)

    def test_spec(self, rc):
        spec = rc.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in rc.spec()

    def test_watch(self, rc):
        assert 'test/watch' not in rc.meta.labels
        with rc.watch() as watcher:
            rc.meta.labels.set('test/watch', 'val')
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
        assert isinstance(
            update.item, _replicationcontroller.ReplicationControllerItem)

    def test_observed_replicas(self, rc):
        assert rc.observed_replicas == rc.spec()['replicas']

    def test_observed_generation(self, rc):
        assert rc.observed_generation == rc.raw['status']['observedGeneration']

    def test_fully_labeled_replicas(self, rc):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                replicas = rc.fully_labeled_replicas
            except _error.StatusError:
                pass
            else:
                break
        else:
            pytest.fail('No fully labeled replicas found')
        assert replicas == rc.spec()['replicas']

    def test_ready_replicas(self, rc):
        assert rc.ready_replicas == rc.raw['status']['readyReplicas']

    def test_available_replicas(self, rc):
        assert rc.available_replicas == rc.raw['status']['availableReplicas']

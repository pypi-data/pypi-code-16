import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _replicaset
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


@pytest.fixture(scope='module')
def pause(request, cluster):
    """A replica set running the pause container."""
    data = {
        'apiVersion': 'v1',
        'kind': 'ReplicaSet',
        'metadata': {
            'generateName': 'test-pause-',
            'labels': {
                'test/rs': 'pause',
            },
            'namespace': 'default',
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'test/rs': 'pause',
                },
            },
            'template': {
                'metadata': {
                    'labels': {
                        'test/rs': 'pause',
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
                             'default', 'replicasets', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'replicasets', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestReplicaSetView:

    @pytest.fixture
    def rsview(self, cluster):
        """A ReplicaSetView instance."""
        return _replicaset.ReplicaSetView(cluster)

    def test_replicasetview(self, rsview):
        assert isinstance(rsview, _base.ViewABC)
        assert rsview.namespace is None

    def test_create_namespace(self, cluster):
        view = _replicaset.ReplicaSetView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, rsview):
        assert rsview.kind is _base.Kind.ReplicaSetList

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_iter_type(self, cluster, pause, ns):  # pylint: disable=unused-argument
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _replicaset.ReplicaSetView(cluster, namespace=ns)
        uids = []
        for rs in view:
            assert isinstance(rs, _replicaset.ReplicaSetItem)
            assert rs.meta.uid not in uids
            uids.append(rs.meta.uid)
        assert uids

    def test_fetch(self, rsview, pause):
        name = pause['metadata']['name']
        rs = rsview.fetch(name, namespace='default')
        assert isinstance(rs, _base.ItemABC)
        assert rs.meta.name == name

    def test_fetch_no_ns(self, rsview, pause):
        with pytest.raises(_error.NamespaceError):
            rsview.fetch(pause['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, pause):
        view = _replicaset.ReplicaSetView(
            cluster, namespace=pause['metadata']['namespace'])
        rs = view.fetch(pause['metadata']['name'])
        assert isinstance(rs, _base.ItemABC)
        assert rs.meta.uid == pause['metadata']['uid']

    def test_fetch_no_item(self, rsview):
        with pytest.raises(LookupError):
            rsview.fetch('this-rs-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize('filt', [{'test/rs': 'pause'}, 'test/rs=pause'])
    def test_filter_labels(self, rsview, pause, filt):
        items = rsview.filter(labels=filt)
        assert pause['metadata']['uid'] in {rs.meta.uid for rs in items}

    def test_filter_fields_dict(self, rsview, pause):
        fields = {'metadata.name': pause['metadata']['name']}
        items = list(rsview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    def test_filter_fields_str(self, rsview, pause):
        fields = 'metadata.name={pause.metadata.name}'.format(pause=pause)
        items = list(rsview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_watch(self, request, cluster, pause, ns):    # pylint: disable=too-many-branches
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _replicaset.ReplicaSetView(cluster, namespace=ns)
        rs = view.fetch(pause['metadata']['name'],
                        namespace=pause['metadata']['namespace'])
        assert 'test/foo' not in rs.meta.labels
        request.addfinalizer(lambda: rs.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            rs.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _replicaset.ReplicaSetItem)


class TestReplicaSetItem:

    @pytest.fixture
    def rs(self, cluster, pause):
        """The pause ReplicaSet."""
        return cluster.replicasets.fetch(
            pause['metadata']['name'],
            namespace=pause['metadata']['namespace'])

    def test_replicaset(self, cluster, rs):
        assert rs.cluster is cluster

    def test_kind(self, rs):
        assert rs.kind is _base.Kind.ReplicaSet

    def test_raw(self, rs):
        assert isinstance(rs.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            rs.raw['foo'] = 'bar'

    def test_fetch(self, rs):
        rs1 = rs.fetch()
        assert rs != rs1
        assert rs.meta.uid == rs1.meta.uid

    def test_meta(self, rs):
        assert isinstance(rs.meta, _meta.ObjectMeta)

    def test_spec(self, rs):
        spec = rs.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in rs.spec()

    def test_watch(self, rs):
        assert 'test/watch' not in rs.meta.labels
        with rs.watch() as watcher:
            rs.meta.labels.set('test/watch', 'val')
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
        assert isinstance(update.item, _replicaset.ReplicaSetItem)

    def test_observed_replicas(self, rs):
        assert rs.observed_replicas == rs.spec()['replicas']

    def test_observed_generation(self, rs):
        assert rs.observed_generation == rs.raw['status']['observedGeneration']

    def test_fully_labeled_replicas(self, rs):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                replicas = rs.fully_labeled_replicas
            except _error.StatusError:
                pass
            else:
                break
        else:
            pytest.fail('No fully labeled replicas found')
        assert replicas == rs.spec()['replicas']

import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _namespace
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


class TestNamespaceView:

    @pytest.fixture
    def nsview(self, cluster):
        """Return a NamespaceView instance."""
        return _namespace.NamespaceView(cluster)

    def test_nodeview(self, nsview):
        assert isinstance(nsview, _base.ViewABC)

    def test_create_view(self, cluster):
        with pytest.raises(_error.NamespaceError):
            _namespace.NamespaceView(cluster, namespace='oops')

    def test_kind(self, nsview):
        assert nsview.kind is _base.Kind.NamespaceList

    def test_iter_type(self, nsview):
        names = []
        for ns in nsview:
            assert isinstance(ns, _namespace.NamespaceItem)
            assert ns.meta.name not in names
            names.append(ns.meta.name)
        assert names

    def test_fetch(self, nsview):
        srcnode = next(iter(nsview))
        ns = nsview.fetch(srcnode.meta.name)
        assert isinstance(ns, _namespace.NamespaceItem)
        assert ns.meta.name == srcnode.meta.name

    def test_fetch_namespace(self, nsview):
        with pytest.raises(_error.NamespaceError):
            nsview.fetch('foo', namespace='oops')

    def test_fetch_no_item(self, nsview):
        with pytest.raises(LookupError):
            nsview.fetch('this-ns-does-not-exist-i-would-really-hope')

    def test_filter_labels(self, request, nsview):
        srcns = next(iter(nsview))
        assert 'test/foo' not in srcns.meta.labels
        request.addfinalizer(lambda: srcns.meta.labels.delete('test/foo'))
        srcns.meta.labels.set('test/foo', 'val')
        namespaces = [ns for ns in nsview
                      if ns.meta.labels.get('test/foo') == 'val']
        namespaces.sort()
        assert namespaces
        labelsel = {'test/foo': 'val'}
        selected = list(nsview.filter(labels=labelsel))
        selected.sort()
        for orig, found in zip(namespaces, selected):
            assert orig.meta.uid == found.meta.uid

    def test_filter_fields(self, request, nsview):
        srcns = next(iter(nsview))
        sel = {'metadata.uid': srcns.meta.uid}
        if request.config.getoption('verify'):
            # I can't seem to find an attribute which k8s wants to filter
            # on.  Maybe one just can't filter a namespace.
            with pytest.raises(_error.APIError) as err:
                list(nsview.filter(fields=sel))
            assert err.value.status_code == 400
        else:
            namespaces = list(nsview.filter(fields=sel))
            assert len(namespaces) == 1
            assert namespaces[0].meta.name == srcns.meta.name

    def test_watch(self, request, nsview):
        ns = next(iter(nsview))
        assert 'test/foo' not in ns.meta.labels
        request.addfinalizer(lambda: ns.meta.labels.delete('test/foo'))
        with nsview.watch() as watcher:
            ns.meta.labels.set('test/foo', 'val')
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    update = watcher.next(timeout=0.2)
                except TimeoutError:
                    continue
                except StopIteration:
                    pytest.fail('Watch iterator exhousted')
                else:
                    if 'test/foo' in update.item.meta.labels:
                        break
            else:
                pytest.fail('New labels not found')
        assert isinstance(update, _watch.WatchEvent)
        assert isinstance(update.evtype, _watch.WatchEventType)
        assert isinstance(update.item, _namespace.NamespaceItem)


class TestNamespaceItem:

    @pytest.fixture
    def ns(self, cluster):
        return next(iter(cluster.namespaces))

    def test_ns(self, ns):
        assert isinstance(ns, _base.ItemABC)
        assert isinstance(ns, _namespace.NamespaceItem)

    def test_cluster(self, cluster, ns):
        assert ns.cluster is cluster

    def test_kind(self, ns):
        assert ns.kind == _base.Kind.Namespace

    def test_raw(self, ns):
        assert isinstance(ns.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            ns.raw['foo'] = 'bar'

    def test_fetch(self, ns):
        ns1 = ns.fetch()
        assert ns1 != ns
        assert ns.meta.uid == ns1.meta.uid

    def test_spec(self, ns):
        spec = ns.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' in spec
        assert 'foo' not in ns.spec()

    def test_phase(self, ns):
        assert isinstance(ns.phase, _namespace.NamespacePhase)
        assert isinstance(ns.phase, ns.NamespacePhase)

    def test_watch(self, request, ns):
        assert 'test/foo' not in ns.meta.labels
        def fin():
            curr_ns = ns.cluster.namespaces.fetch(ns.meta.name)
            if 'test/foo' in curr_ns.meta.labels:
                curr_ns.meta.labels.delete('test/foo')
        request.addfinalizer(fin)
        with ns.watch() as watcher:
            ns.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _namespace.NamespaceItem)

    def test_delete_idempotence_on_409(self, ns, monkeypatch):
        def delete(*path):    # pylint: disable=unused-argument
            class Resource:
                status_code = 409
            raise _error.APIError(Resource, 'msg')
        monkeypatch.setattr(ns.cluster.proxy, 'delete', delete)
        assert ns.delete() is None

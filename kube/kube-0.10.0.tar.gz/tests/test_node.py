import collections
import ipaddress
import time

import pytest

import kube
from kube import _base
from kube import _error
from kube import _meta
from kube import _node
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


class TestNodeView:

    @pytest.fixture
    def nodeview(self, cluster):
        """Return a NodeView instance."""
        return cluster.nodes

    def test_nodeview(self, nodeview):
        assert isinstance(nodeview, _base.ViewABC)
        assert isinstance(nodeview, _node.NodeView)

    def test_create_namespace(self, cluster):
        with pytest.raises(_error.NamespaceError):
            _node.NodeView(cluster, namespace='oops')

    def test_kind(self, nodeview):
        assert nodeview.kind is _base.Kind.NodeList

    def test_iter_type(self, nodeview):
        nodenames = []
        for node in nodeview:
            assert isinstance(node, _node.NodeItem)
            assert node.meta.name not in nodenames
            nodenames.append(node.meta.name)
        assert nodenames

    def test_fetch(self, nodeview):
        srcnode = next(iter(nodeview))
        node = nodeview.fetch(srcnode.meta.name)
        assert isinstance(node, _node.NodeItem)
        assert node.meta.name == srcnode.meta.name

    def test_fetch_namespace(self, nodeview):
        with pytest.raises(_error.NamespaceError):
            nodeview.fetch('foo', namespace='oops')

    def test_fetch_no_item(self, nodeview):
        with pytest.raises(LookupError):
            nodeview.fetch('this-node-does-not-exist-i-would-really-hope')

    def test_filter_labels(self, nodeview):
        srcnode = next(iter(nodeview))
        assert 'kubernetes.io/hostname' in srcnode.meta.labels
        labelval = srcnode.meta.labels['kubernetes.io/hostname']
        nodes = [n for n in nodeview
                 if n.meta.labels['kubernetes.io/hostname'] == labelval]
        nodes.sort()
        assert nodes
        labelsel = {'kubernetes.io/hostname': labelval}
        selected = list(nodeview.filter(labels=labelsel))
        selected.sort()
        for orig_node, found_node in zip(nodes, selected):
            assert orig_node.meta.uid == found_node.meta.uid

    def test_filter_fields(self, nodeview):
        srcnode = next(iter(nodeview))
        sel = {'metadata.name': srcnode.meta.name}
        nodes = list(nodeview.filter(fields=sel))
        assert len(nodes) == 1
        assert nodes[0].meta.name == srcnode.meta.name

    def test_watch(self, request, nodeview):
        node = next(iter(nodeview))
        assert 'test/foo' not in node.meta.labels
        watcher = nodeview.watch()
        request.addfinalizer(watcher.close)
        request.addfinalizer(lambda: node.meta.labels.delete('test/foo'))
        node.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _node.NodeItem)


class TestNodeResource:

    @pytest.fixture
    def node(self, cluster):
        return next(iter(cluster.nodes))

    def test_node(self, node):
        assert isinstance(node, _base.ItemABC)
        assert isinstance(node, _node.NodeItem)

    def test_cluster(self, cluster, node):
        assert node.cluster is cluster

    def test_kind(self, node):
        assert node.kind == _base.Kind.Node

    def test_raw(self, node):
        assert isinstance(node.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            node.raw['foo'] = 'bar'

    def test_fetch(self, node):
        node1 = node.fetch()
        assert node != node1
        assert node.meta.uid == node1.meta.uid

    def test_meta(self, node):
        assert isinstance(node.meta, _meta.ObjectMeta)

    def test_spec(self, node):
        # This also tests that changing the spec does not affect .raw
        assert isinstance(node.spec(), dict)
        assert 'foo' not in node.spec()
        node.spec()['foo'] = 'bar'
        assert 'foo' not in node.spec()

    def test_addresses(self, node):
        assert len(list(node.addresses)) > 0
        for addr in node.addresses:
            assert isinstance(addr.type, kube.AddressType)
            if addr.type == kube.AddressType.Hostname:
                assert isinstance(addr.addr, str)
            else:
                assert isinstance(addr.addr,
                                  (ipaddress.IPv4Address,
                                   ipaddress.IPv6Address))

    @pytest.mark.xfail
    def test_capacity(self, node):
        assert node.capacity

    @pytest.mark.xfail
    def test_conditions(self, node):
        assert node.conditions

    def test_watch(self, request, node):
        assert 'test/foo' not in node.meta.labels
        watcher = node.watch()
        request.addfinalizer(watcher.close)
        request.addfinalizer(lambda: node.meta.labels.delete('test/foo'))
        node.meta.labels.set('test/foo', 'val')
        update = watcher.next(timeout=1)
        while True:
            try:
                update = watcher.next(timeout=1)
            except (TimeoutError, StopIteration):
                break
        assert 'test/foo' in update.item.meta.labels

    def test_watch_contextmgr(self, request, node):
        assert 'test/foo' not in node.meta.labels
        request.addfinalizer(lambda: node.meta.labels.delete('test/foo'))
        with node.watch() as watcher:
            assert watcher._watcher._sock.fileno() >= 0
        assert watcher._watcher._sock.fileno() == -1

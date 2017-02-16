import collections.abc
import datetime

import pytest

import kube._base
from kube import _meta as meta
from kube import _util


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


class DummyResource(kube._base.ItemABC):
    """Just a dummy ItemABC implementation.

    Only the meta property and raw attribute matter.
    """
    kind = None
    resource = None
    api_paths = None
    cluster = None
    raw = None

    def __init__(self):         # pylint: disable=super-init-not-called
        self.raw = {
            'metadata': {
                'name': 'foobar',
                'namespace': 'default',
                'labels': {
                    'foo': 'bar',
                },
                'resourceVersion': '2599407',
                'creationTimestamp': '2009-02-13T23:31:30Z',
                'selfLink': '/api/v1/objs/foobar',
                'uid': 'abc123',
            },
        }

    def fetch(self):
        pass

    @property
    def meta(self):
        return meta.ObjectMeta(self)

    def spec(self):
        pass

    def watch(self):
        pass

    def delete(self):
        pass


@pytest.fixture
def obj():
    return DummyResource()


def test_name(obj):
    assert obj.meta.name == 'foobar'


def test_namespace(obj):
    assert obj.meta.namespace == 'default'


def test_namespace_missing(obj):
    del obj.raw['metadata']['namespace']
    assert obj.meta.namespace is None


def test_eq(obj):
    assert obj.meta == obj.meta


def test_eq_other(obj):
    assert obj.meta != None


def test_labels(obj):
    assert isinstance(obj.meta.labels, collections.abc.Mapping)
    assert 'foo' in obj.meta.labels
    assert obj.meta.labels['foo'] == 'bar'
    assert len(obj.meta.labels) == 1
    for label in obj.meta.labels:
        assert label == 'foo'


def test_labels_dict(obj):
    d = dict(obj.meta.labels)
    assert d['foo'] == 'bar'
    d['hello'] = 1
    assert 'hello' in d
    assert 'hello' not in obj.meta.labels


def test_labels_set(obj):
    assert 'hello' not in obj.meta.labels
    with pytest.raises(TypeError):
        obj.meta.labels['hello'] = 'world'


def test_labels_repr(obj):
    text = repr(obj.meta.labels).lower()
    assert 'labels' in text
    assert 'foo' in text
    assert 'bar' in text


def test_version(obj):
    assert obj.meta.version


def test_created(obj):
    assert isinstance(obj.meta.created, datetime.datetime)
    assert obj.meta.created == datetime.datetime.fromtimestamp(1234567890)


def test_link(obj):
    assert obj.meta.link == '/api/v1/objs/foobar'


def test_uid(obj):
    assert obj.meta.uid == 'abc123'


class TestCluster:
    # Test using real objects in a cluster.

    @pytest.fixture
    def obj(self, request, cluster):
        data = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'generateName': 'testns-',
                'labels': {
                    'foo': 'val',
                },
            },
        }
        ret = cluster.proxy.post('api/v1', 'namespaces', json=data)
        name = ret['metadata']['name']
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces', name)
        request.addfinalizer(fin)
        return cluster.namespaces.fetch(name)

    def test_existing_label(self, obj):
        assert 'foo' in obj.meta.labels

    def test_no_labels(self, obj):
        for label in obj.meta.labels:
            obj = obj.meta.labels.delete(label)
        assert len(obj.meta.labels) == 0


class TestResourceLabelsMod:
    # Test modifying the ResrouceLabels.  The plain read-only mapping
    # behaviour is tested above already.

    @pytest.fixture
    def obj(self, request, cluster):
        """An generic resource object.

        The object will not have any labels starting with the "test/"
        prefix and any labels with this prefix will be removed after
        the test.  There is a minor chicken and egg issue here, so if
        functionality breaks this might be a bit confusing to debug.
        """
        node = next(iter(cluster.nodes))
        for label in node.meta.labels:
            assert not label.startswith('test/')
        def fin():
            obj = node.fetch()
            for label in list(obj.meta.labels.keys()):
                if label.startswith('test/'):
                    obj.meta.labels.delete(label)
        request.addfinalizer(fin)
        return node

    def test_obj(self, obj):
        assert isinstance(obj.meta.labels, meta.ResourceLabels)

    def test_set(self, obj):
        ret = obj.meta.labels.set('test/foo', 'bar')
        assert isinstance(ret, obj.__class__)
        assert ret.meta.labels['test/foo'] == 'bar'
        new = obj.fetch()
        assert new.meta.labels['test/foo'] == 'bar'
        assert 'test/foo' not in obj.meta.labels

    def test_delete(self, obj):
        new0 = obj.meta.labels.set('test/foo', 'bar')
        assert new0.meta.labels['test/foo'] == 'bar'
        ret = obj.meta.labels.delete('test/foo')
        assert 'test/foo' not in ret.meta.labels
        new1 = obj.fetch()
        assert 'test/foo' not in new1.meta.labels
        assert 'test/foo' in new0.meta.labels

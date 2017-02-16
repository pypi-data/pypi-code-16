import time

import pyrsistent
import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


@pytest.fixture(autouse=True)
def find_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


class TestBaseView:

    @pytest.fixture
    def concrete(self):
        """A concrete subclass of :class:`kube._base.BaseView`.

        The abstract methods are replaced by mocks. The ``cluster`` and
        ``namespace`` attributes are set on the class and default to ``None``.
        """
        return type("Concrete", (_base.BaseView,), {
            '__init__': lambda *a, **kw: None,
            '__iter__': lambda *a, **kw: None,
            'fetch': lambda *a, **kw: None,
            'filter': lambda *a, **kw: None,
            'watch': lambda *a, **kw: None,
            'cluster': None,
            'namespace': None,
            'kind': 'Foo',
            'resource': 'foos',
        })

    def test_repr(self, concrete):
        assert repr(concrete()) == '<Concrete>'

    def test_repr_with_namespace(self, concrete):
        view = concrete()
        view.namespace = 'bar'
        assert repr(view) == '<Concrete namespace=bar>'


class TestBaseItem:

    @pytest.fixture(params=['ns', 'no-ns'])
    def item(self, request, cluster):
        """A real item implementation.

        This is parameterised, once for an item in a namespace and
        once for an item without a namespace.
        """
        if request.param == 'ns':
            data = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'generateName': 'testitem-',
                },
                'namespace': 'default',
            }
            item = cluster.create(data, namespace='default')
        else:
            data = {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'generateName': 'testitem-',
                },
            }
            item = cluster.create(data)
        request.addfinalizer(item.delete)
        return item

    def test_repr(self, item):
        assert item.meta.name in repr(item)
        if item.meta.namespace:
            assert 'namespace={}'.format(item.meta.namespace) in repr(item)

    def test_cluster(self, cluster, item):
        assert item.cluster is cluster

    def test_raw(self, item):
        assert isinstance(item.raw, pyrsistent.PMap)

    def test_meta(self, item):
        assert isinstance(item.meta, _meta.ObjectMeta)
        assert item.meta.name.startswith('testitem-')

    def test_spec(self, item):
        spec = item.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'spam'
        assert 'foo' not in item.spec()

    def test_fetch(self, item):
        new = item.fetch()
        assert new is not item
        assert new != item
        assert new.meta.uid == item.meta.uid

    def test_fetch_error(self, item, monkeypatch):
        def get(*path):    # pylint: disable=unused-argument
            class Resource:
                status_code = 400
            raise _error.APIError(Resource, 'msg')
        monkeypatch.setattr(item.cluster.proxy, 'get', get)
        with pytest.raises(_error.APIError):
            item.fetch()

    def test_watch(self, item):
        assert 'test/watch' not in item.meta.labels
        with item.watch() as watcher:
            item.meta.labels.set('test/watch', 'val')
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    update = watcher.next(timeout=0.2)
                except TimeoutError:
                    continue
                except StopIteration:
                    pytest.fail('Watch interator exhausted')
                else:
                    if 'test/watch' in update.item.meta.labels:
                        break
            else:
                pytest.fail('New label not found')
        assert isinstance(update, _watch.WatchEvent)
        assert isinstance(update.evtype, _watch.WatchEventType)
        assert isinstance(update.item, item.__class__)

    def test_delete(self, item):
        # Deleting a namespace takes a long time.
        item.delete()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                item.fetch()
            except LookupError:
                break
            time.sleep(0.3)
        else:
            pytest.fail('Did not raise LookupError')

    def test_delete_idempotence(self, item):
        item.delete()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                item.fetch()
            except LookupError:
                break
            time.sleep(0.3)
        else:
            pytest.fail('Test inconclusive, failed to delete resource')
        assert item.delete() is None

    def test_delete_error(self, item, monkeypatch):
        def delete(*path):    # pylint: disable=unused-argument
            class Resource:
                status_code = 400  # i.e. not 404
            raise _error.APIError(Resource, 'msg')
        monkeypatch.setattr(item.cluster.proxy, 'delete', delete)
        with pytest.raises(_error.APIError):
            item.delete()
        monkeypatch.undo()

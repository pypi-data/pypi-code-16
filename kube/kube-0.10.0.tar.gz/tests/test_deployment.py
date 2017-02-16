import collections
import time

import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _deployment
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
        'kind': 'Deployment',
        'metadata': {
            'generateName': 'test-pause-',
            'labels': {
                'test/deploy': 'pause',
            },
            'namespace': 'default',
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'test/deploy': 'pause',
                },
            },
            'template': {
                'metadata': {
                    'labels': {
                        'test/deploy': 'pause',
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
                             'default', 'deployments', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'deployments', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


class TestDeploymentView:

    @pytest.fixture
    def deployview(self, cluster):
        """A DeploymentView instance."""
        return _deployment.DeploymentView(cluster)

    def test_deploymentview(self, deployview):
        assert isinstance(deployview, _base.ViewABC)
        assert deployview.namespace is None

    def test_create_namespace(self, cluster):
        view = _deployment.DeploymentView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, deployview):
        assert deployview.kind is _base.Kind.DeploymentList

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_iter_type(self, cluster, pause, ns):  # pylint: disable=unused-argument
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _deployment.DeploymentView(cluster, namespace=ns)
        uids = []
        for deploy in view:
            assert isinstance(deploy, _deployment.DeploymentItem)
            assert deploy.meta.uid not in uids
            uids.append(deploy.meta.uid)
        assert uids

    def test_fetch(self, deployview, pause):
        name = pause['metadata']['name']
        deploy = deployview.fetch(name, namespace='default')
        assert isinstance(deploy, _base.ItemABC)
        assert deploy.meta.name == name

    def test_fetch_no_ns(self, deployview, pause):
        with pytest.raises(_error.NamespaceError):
            deployview.fetch(pause['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, pause):
        view = _deployment.DeploymentView(
            cluster, namespace=pause['metadata']['namespace'])
        deploy = view.fetch(pause['metadata']['name'])
        assert isinstance(deploy, _base.ItemABC)
        assert deploy.meta.uid == pause['metadata']['uid']

    def test_fetch_no_item(self, deployview):
        with pytest.raises(LookupError):
            deployview.fetch(
                'this-deploy-does-not-exist-i-hope', namespace='foo')

    @pytest.mark.parametrize(
        'filt', [{'test/deploy': 'pause'}, 'test/deploy=pause'])
    def test_filter_labels(self, deployview, pause, filt):
        items = deployview.filter(labels=filt)
        assert pause['metadata']['uid'] in {
            deploy.meta.uid for deploy in items}

    def test_filter_fields_dict(self, deployview, pause):
        fields = {'metadata.name': pause['metadata']['name']}
        items = list(deployview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    def test_filter_fields_str(self, deployview, pause):
        fields = 'metadata.name={pause.metadata.name}'.format(pause=pause)
        items = list(deployview.filter(fields=fields))
        assert len(items) == 1
        assert items[0].meta.uid == pause['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_watch(self, request, cluster, pause, ns):    # pylint: disable=too-many-branches
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        view = _deployment.DeploymentView(cluster, namespace=ns)
        deploy = view.fetch(pause['metadata']['name'],
                            namespace=pause['metadata']['namespace'])
        assert 'test/foo' not in deploy.meta.labels
        request.addfinalizer(lambda: deploy.meta.labels.delete('test/foo'))
        with view.watch() as watcher:
            deploy.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _deployment.DeploymentItem)


class TestDeploymentItem:

    @pytest.fixture
    def deploy(self, cluster, pause):
        """The pause Deployment."""
        return cluster.deployments.fetch(
            pause['metadata']['name'],
            namespace=pause['metadata']['namespace'])

    def test_deployment(self, cluster, deploy):
        assert deploy.cluster is cluster

    def test_kind(self, deploy):
        assert deploy.kind is _base.Kind.Deployment

    def test_raw(self, deploy):
        assert isinstance(deploy.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            deploy.raw['foo'] = 'bar'

    def test_fetch(self, deploy):
        deploy1 = deploy.fetch()
        assert deploy != deploy1
        assert deploy.meta.uid == deploy1.meta.uid

    def test_meta(self, deploy):
        assert isinstance(deploy.meta, _meta.ObjectMeta)

    def test_spec(self, deploy):
        spec = deploy.spec()
        assert isinstance(spec, dict)
        assert 'foo' not in spec
        spec['foo'] = 'bar'
        assert 'foo' not in deploy.spec()

    def test_watch(self, deploy):
        assert 'test/watch' not in deploy.meta.labels
        with deploy.watch() as watcher:
            deploy.meta.labels.set('test/watch', 'val')
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
        assert isinstance(update.item, _deployment.DeploymentItem)

    def test_replicas(self, deploy):
        assert deploy.observed_replicas == deploy.raw['status']['replicas']

    def test_observed_generation(self, deploy):
        assert deploy.observed_generation == \
               deploy.raw['status']['observedGeneration']

    def test_updated_replicas(self, deploy):
        assert deploy.updated_replicas == \
               deploy.raw['status']['updatedReplicas']

    def test_available_replicas(self, deploy):
        assert deploy.available_replicas == \
               deploy.raw['status']['availableReplicas']

    def test_unavailable_replicas(self, deploy):
        assert deploy.unavailable_replicas == \
               deploy.raw['status']['unavailableReplicas']

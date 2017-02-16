import collections
import datetime
import ipaddress
import time

import pyrsistent
import pytest

from kube import _base
from kube import _error
from kube import _meta
from kube import _pod
from kube import _util
from kube import _watch


@pytest.fixture(scope='module')
def pause(request, cluster):
    """A pod running the kubernetes/pause container.

    This is a tiny container which does nothing at all.  It is
    useful in tests as at least we will be certain there will be
    one pod on the cluster.
    """
    data = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'generateName': 'test-pause-',
            'labels': {
                'test/pod': 'pause',
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
    }
    ret = cluster.proxy.post('api/v1', 'namespaces',
                             'default', 'pods', json=data)
    def fin():
        cluster.proxy.delete('api/v1', 'namespaces', 'default',
                             'pods', ret['metadata']['name'])
    request.addfinalizer(fin)
    return ret


@pytest.fixture(autouse=True)
def no_finding_api_path(monkeypatch):
    monkeypatch.setattr(_util, 'find_api_path', lambda x, y, z: 'api/v1')


class TestPodView:

    @pytest.fixture
    def podview(self, cluster):
        """Return a PodView instance."""
        return _pod.PodView(cluster)

    def test_podview(self, podview):
        assert isinstance(podview, _base.ViewABC)

    def test_create_namespace(self, cluster):
        view = _pod.PodView(cluster, namespace='default')
        assert view.namespace == 'default'

    def test_kind(self, podview):
        assert podview.kind is _base.Kind.PodList

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_iter_type(self, cluster, pause, ns):
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        podview = _pod.PodView(cluster, namespace=ns)
        uids = []
        for pod in podview:
            assert isinstance(pod, _pod.PodItem)
            assert pod.meta.uid not in uids
            uids.append(pod.meta.uid)
        assert uids

    def test_fetch(self, podview, pause):
        name = pause['metadata']['name']
        pod = podview.fetch(name, namespace='default')
        assert isinstance(pod, _base.ItemABC)
        assert pod.meta.name == name

    def test_fetch_no_ns(self, podview, pause):
        with pytest.raises(_error.NamespaceError):
            podview.fetch(pause['metadata']['name'])

    def test_fetch_view_with_ns(self, cluster, pause):
        view = _pod.PodView(cluster, namespace=pause['metadata']['namespace'])
        pod = view.fetch(pause['metadata']['name'])
        assert isinstance(pod, _base.ItemABC)
        assert pod.meta.uid == pause['metadata']['uid']

    def test_fetch_no_item(self, podview):
        with pytest.raises(LookupError):
            podview.fetch('this-pod-does-not-exist-i-hope', namespace='foo')

    def test_filter_labels_dict(self, podview, pause):
        pods = podview.filter(labels={'test/pod': 'pause'})
        assert pause['metadata']['uid'] in {p.meta.uid for p in pods}

    def test_filter_labels_str(self, podview, pause):
        pods = podview.filter(labels='test/pod=pause')
        assert pause['metadata']['uid'] in {p.meta.uid for p in pods}

    def test_filter_fields_dict(self, podview, pause):
        fields = {
            'metadata.name': pause['metadata']['name'],
        }
        pods = list(podview.filter(fields=fields))
        assert len(pods) == 1
        assert pods[0].meta.uid == pause['metadata']['uid']

    def test_filter_fields_str(self, podview, pause):
        fields = 'metadata.name={pause.metadata.name}'.format(pause=pause)
        pods = list(podview.filter(fields=fields))
        assert len(pods) == 1
        assert pods[0].meta.uid == pause['metadata']['uid']

    @pytest.mark.parametrize('ns', [None, 'pause'])
    def test_watch(self, cluster, pause, ns):
        # pylint: disable=too-many-branches
        if ns == 'pause':
            ns = pause['metadata']['namespace']
        podview = _pod.PodView(cluster, namespace=ns)
        pod = podview.fetch(pause['metadata']['name'],
                            namespace=pause['metadata']['namespace'])
        with podview.watch() as watcher:
            pod.meta.labels.set('test/foo', 'val')
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
        assert isinstance(update.item, _pod.PodItem)


class TestPodItem:

    @pytest.fixture
    def pod(self, cluster, pause):
        """The pod for the pause container."""
        return cluster.pods.fetch(pause['metadata']['name'],
                                  namespace=pause['metadata']['namespace'])

    def test_pod(self, pod):
        assert isinstance(pod, _base.ItemABC)
        assert isinstance(pod, _pod.PodItem)

    def test_cluster(self, cluster, pod):
        assert pod.cluster is cluster

    def test_kind(self, pod):
        assert pod.kind is _base.Kind.Pod

    def test_raw(self, pod):
        assert isinstance(pod.raw, collections.abc.Mapping)
        with pytest.raises(TypeError):
            pod.raw['foo'] = 'bar'

    def test_fetch(self, pod):
        pod1 = pod.fetch()
        assert pod != pod1
        assert pod.meta.uid == pod1.meta.uid

    def test_meta(self, pod):
        assert isinstance(pod.meta, _meta.ObjectMeta)

    def test_spec(self, pod):
        assert isinstance(pod.spec(), dict)
        assert 'foo' not in pod.spec()
        pod.spec()['foo'] = 'bar'
        assert 'foo' not in pod.spec()

    def test_phase(self, pod):
        assert isinstance(pod.phase, pod.PodPhase)
        assert isinstance(pod.phase, _pod.PodPhase)

    def test_start_time(self, pod):
        assert isinstance(pod.start_time, datetime.datetime)
        assert pod.start_time < datetime.datetime.utcnow()

    def test_ip(self, pod):
        assert isinstance(pod.ip, (ipaddress.IPv4Address,
                                   ipaddress.IPv6Address))

    def test_host_ip(self, pod):
        assert isinstance(pod.host_ip, (ipaddress.IPv4Address,
                                        ipaddress.IPv6Address))

    def test_message(self, pod):
        with pytest.raises(_error.StatusError):
            pod.message         # pylint: disable=pointless-statement

    def test_reason(self, pod):
        with pytest.raises(_error.StatusError):
            pod.reason          # pylint: disable=pointless-statement

    def test_containers_iter(self, pod):
        containers = list(pod.containers)
        assert containers
        for container in containers:
            assert isinstance(container, _pod.Container)

    def test_watch(self, pod):
        assert 'test/watch' not in pod.meta.labels
        with pod.watch() as watcher:
            pod.meta.labels.set('test/watch', 'val')
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
        assert isinstance(update.item, _pod.PodItem)


class TestContainer:

    @pytest.fixture
    def crun(self, cluster, pause):
        """The running container in our pause pod."""
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            pod = cluster.pods.fetch(pause['metadata']['name'],
                                     namespace=pause['metadata']['namespace'])
            try:
                return next(pod.containers)
            except StopIteration:
                time.sleep(0.2)
        else:                   # pylint: disable=useless-else-on-loop
            pytest.fail('No container found')

    @pytest.fixture(scope='module')
    def cterm(self, request, cluster):
        """A terminated container in a pod."""
        data = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'generateName': 'test-busybox-',
                'labels': {
                    'test/pod': 'busybox',
                    'test/container': 'term',
                },
                'namespace': 'default',
            },
            'spec': {
                'containers': [
                    {
                        'name': 'busybox',
                        'image': 'busybox',
                        'command': ['/bin/sh', '-c', 'exit 0'],
                    },
                ],
                'restartPolicy': 'Never',
            },
        }
        ret = cluster.proxy.post('api/v1', 'namespaces',
                                 'default', 'pods', json=data)
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces',
                                 'default', 'pods', ret['metadata']['name'])
        request.addfinalizer(fin)
        if request.config.getoption('verify'):
            self._wait_container_state(cluster, ret, 'terminated')
        else:
            self._patch_container_state(cluster, ret, 'terminated')
        pod = cluster.pods.fetch(ret['metadata']['name'],
                                 namespace=ret['metadata']['namespace'])
        return next(pod.containers)

    @pytest.fixture(scope='module')
    def cwait(self, request, cluster):
        """A waiting container in a pod.

        This is somewhat brittle, it depends on k8s' CrashLoopBackOff
        to kick in and to get lucky to find the pod in the right
        state.  As time goes on it becomes more and more likely that
        the container will be in the waiting state.
        """
        if request.config.getoption('verify'):
            pytest.skip('This is too brittle')
        data = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'generateName': 'test-busybox-',
                'labels': {
                    'test/pod': 'busybox',
                    'test/container': 'wait',
                },
                'namespace': 'default',
            },
            'spec': {
                'containers': [
                    {
                        'name': 'busybox',
                        'image': 'busybox',
                        'command': ['/bin/sh', '-c', 'exit 1'],
                    },
                ],
                'restartPolicy': 'Always',
            },
        }
        ret = cluster.proxy.post('api/v1', 'namespaces',
                                 'default', 'pods', json=data)
        def fin():
            cluster.proxy.delete('api/v1', 'namespaces',
                                 'default', 'pods', ret['metadata']['name'])
        request.addfinalizer(fin)
        if request.config.getoption('verify'):
            self._wait_container_state(cluster, ret, 'waiting', timeout=32)
        else:
            self._patch_container_state(cluster, ret, 'waiting')
        pod = cluster.pods.fetch(ret['metadata']['name'],
                                 namespace=ret['metadata']['namespace'])
        return next(pod.containers)

    def _wait_container_state(self, cluster, raw, state, timeout=8):
        """Wait for the desired podstate with a timeout."""
        namespace = raw['metadata']['namespace']
        name = raw['metadata']['name']
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(0.2)
            pod = cluster.proxy.get('api/v1', 'namespaces',
                                    namespace, 'pods', name)
            try:
                container_status = pod['status']['containerStatuses'][0]
            except KeyError:
                continue
            if state in container_status['state'].keys():
                break
        else:
            pytest.fail('Container state not found')

    def _patch_container_state(self, cluster, raw, state):
        """Patch the given container state, for StubAPIServerProxy only."""
        # This creates a JSON Merge Patch, not a k8s strategic merge patch.
        container_id = raw['status']['containerStatuses'][0]['containerID'],
        start_time = raw['status']['startTime']
        if state == 'terminated':
            status = pyrsistent.thaw(raw['status']['containerStatuses'][0])
            status['ready'] = False
            status['state'] = {
                'terminated': {
                    'containerID': container_id,
                    'exitCode': 0,
                    'finishedAt': start_time,
                    'reason': 'Error',
                    'startedAt': start_time,
                },
            }
        elif state == 'waiting':
            status = pyrsistent.thaw(raw['status']['containerStatuses'][0])
            status['ready'] = False
            status['state'] = {
                'waiting': {
                    'message': 'Back-off ... restarting failed container=...',
                    'reason': 'CrashLoopBackOff',
                },
            }
            status['lastState'] = {
                'terminated': {
                    'containerID': container_id,
                    'exitCode': 0,
                    'finishedAt': start_time,
                    'reason': 'Error',
                    'startedAt': start_time,
                },
            }
        patch = {'status': {'containerStatuses': [status]}}
        cluster.proxy.patch(raw['metadata']['selfLink'], patch=patch)

    def test_repr(self, crun):
        assert repr(crun)

    def test_eq(self, crun, cterm):
        assert crun == crun
        assert crun != cterm
        assert not crun == 'foo'

    def test_name(self, crun):
        assert crun.name == 'pause'

    def test_ready(self, crun):
        assert crun.ready is True

    def test_not_ready(self, cterm):
        assert cterm.ready is False

    def test_restart_count(self, crun):
        assert crun.restart_count >= 0

    def test_image(self, pause, crun):
        assert crun.image == pause['spec']['containers'][0]['image']

    def test_image_id(self, crun):
        assert crun.image_id

    def test_id(self, crun):
        assert crun.id

    def test_state_running(self, crun):
        assert not crun.state.waiting
        assert crun.state.running
        assert not crun.state.terminated

    def test_state_term(self, cterm):
        assert not cterm.state.waiting
        assert not cterm.state.running
        assert cterm.state.terminated

    def test_state_wait(self, cwait):
        assert cwait.state.waiting
        assert not cwait.state.running
        assert not cwait.state.terminated

    def test_state_reason_running(self, crun):
        with pytest.raises(_error.StatusError):
            crun.state.reason  # pylint: disable=pointless-statement

    def test_state_reason_terminated(self, cterm):
        assert cterm.state.reason

    def test_state_reason_waiting(self, cwait):
        assert cwait.state.reason

    def test_state_message_running(self, crun):
        with pytest.raises(_error.StatusError):
            crun.state.message  # pylint: disable=pointless-statement

    def test_state_message_terminated(self, cterm):
        with pytest.raises(_error.StatusError):
            cterm.state.message  # pylint: disable=pointless-statement

    def test_state_message_waiting(self, cwait):
        assert cwait.state.message

    def test_state_started(self, crun):
        assert isinstance(crun.state.started_at, datetime.datetime)
        assert crun.state.started_at < datetime.datetime.utcnow()

    def test_state_exit_code_run(self, crun):
        with pytest.raises(_error.StatusError):
            crun.state.exit_code  # pylint: disable=pointless-statement

    def test_state_exit_code_term(self, cterm):
        assert cterm.state.exit_code == 0

    def test_state_finished_at_run(self, crun):
        with pytest.raises(_error.StatusError):
            crun.state.finished_at  # pylint: disable=pointless-statement

    def test_state_finished_at_term(self, cterm):
        assert isinstance(cterm.state.finished_at, datetime.datetime)
        assert cterm.state.finished_at < datetime.datetime.utcnow()

    def test_state_container_id_run(self, crun):
        with pytest.raises(_error.StatusError):
            crun.state.container_id  # pylint: disable=pointless-statement

    def test_state_container_id_term(self, cterm):
        assert cterm.state.container_id

    def test_state_signal(self, crun):
        with pytest.raises(_error.StatusError):
            assert crun.state.signal

    def test_last_state_run(self, crun):
        with pytest.raises(_error.StatusError):
            assert crun.last_state.running

    def test_last_state_wait(self, cwait):
        assert isinstance(cwait.last_state, _pod.ContainerState)


class TestContainerState:
    # A few artificial tests not covered in the TestContainer tests
    # above.

    def test_repr(self):
        raw = {'running': {'startedAt': '2016-04-12T02:28:52Z'}}
        state = _pod.ContainerState(raw)
        assert repr(state)

    def test_multistate(self):
        running = {
            'startedAt': '2016-04-12T02:28:52Z',
        }
        waiting = {
            'message': 'Back-off ... restarting failed container=...',
            'reason': 'CrashLoopBackOff',
        },
        terminated = {
            'containerID': 'docker://abc',
            'exitCode': 0,
            'finishedAt': '2016-04-12T02:28:52Z',
            'reason': 'Error',
            'startedAt': '2016-04-12T02:28:52Z',
        }
        _pod.ContainerState({'running': running, 'waiting': waiting})
        _pod.ContainerState({'running': running, 'terminated': terminated})
        _pod.ContainerState({'terminated': terminated, 'waiting': waiting})
        with pytest.raises(ValueError):
            _pod.ContainerState({'running': running,
                                 'waiting': waiting,
                                 'terminated': terminated})

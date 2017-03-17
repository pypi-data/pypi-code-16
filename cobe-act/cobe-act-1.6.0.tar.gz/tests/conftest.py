import pytest

import yaml
import time
import os
import base64
import re
import pathlib
import subprocess
import json


@pytest.fixture(scope='session')
def session_id():
    id_ = 'pytest-' + base64.urlsafe_b64encode(os.urandom(6)).decode().lower()
    return id_.replace('_', '')


@pytest.yield_fixture
def kubernetes_namespace(request, tmpdir, session_id):
    namespace = '{1}-{0}'.format(
        re.sub(r'[^a-z0-9]', '-', request.node.name),
        session_id,
    )
    if namespace.endswith('-'):
        namespace = namespace[:-1]
    yaml_path = pathlib.Path(str(tmpdir)) / 'namespace.yaml'
    with yaml_path.open('w') as yaml_fp:
        yaml_namespace = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': namespace,
            },
        }
        yaml.dump(yaml_namespace, yaml_fp)
    subprocess.Popen(
        ['kubectl', 'create', '-f', str(yaml_path), '--context=cobetest'])
    time.sleep(2)
    yield namespace
    subprocess.Popen(
        ['kubectl', 'delete', 'ns', namespace, '--context=cobetest'])


@pytest.yield_fixture
def kubernetes_headless_service(tmpdir, kubernetes_namespace):
    selector_labels = {'select': kubernetes_namespace}
    yaml_path = pathlib.Path(str(tmpdir)) / 'service.yaml'
    with yaml_path.open('w') as yaml_fp:
        yaml_service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'service',
                'namespace': kubernetes_namespace,
            },
            'spec': {
                'clusterIP': 'None',
                'ports': [{
                    'name': 'service',
                    'protocol': 'TCP',
                    'port': 9001,
                }],
                'selector': selector_labels,
            },
        }
        yaml.dump(yaml_service, yaml_fp)
    subprocess.Popen(
        ['kubectl', 'create', '-f', str(yaml_path), '--context=cobetest'])
    time.sleep(2)
    yield selector_labels
    subprocess.Popen([
        'kubectl',
        'delete',
        'svc',
        'service',
        '--namespace',
        kubernetes_namespace,
        '--context=cobetest',
    ])


@pytest.yield_fixture
def kubernetes_pods(tmpdir, kubernetes_namespace, kubernetes_headless_service):
    pod_names = []
    for index in range(3):
        pod_name = 'pod-{}'.format(index)
        pod_names.append(pod_name)
        yaml_path = pathlib.Path(str(tmpdir)) / '{}.yaml'.format(pod_name)
        with yaml_path.open('w') as yaml_fp:
            yaml_service = {
                'apiVersion': 'v1',
                'kind': 'Pod',
                'metadata': {
                    'name': pod_name,
                    'namespace': kubernetes_namespace,
                    'labels': kubernetes_headless_service,
                },
                'spec': {
                    'containers': [{
                        'name': 'bash',
                        'image': 'eu.gcr.io/cobesaas/debian:jessie',
                        'command': ['sleep', 'infinity'],
                    }],
                },
            }
            yaml.dump(yaml_service, yaml_fp)
        subprocess.Popen(
            ['kubectl', 'create', '-f', str(yaml_path), '--context=cobetest'])
    time.sleep(2)
    yield
    for pod_name in pod_names:
        subprocess.Popen([
            'kubectl',
            'delete',
            'pod',
            pod_name,
            '--namespace',
            kubernetes_namespace,
            '--context=cobetest',
        ])


@pytest.yield_fixture
def kubernetes_dns(kubernetes_namespace):
    kube_dns_pods = json.loads(subprocess.Popen([
        'kubectl',
        'get',
        'po',
        '--namespace',
        'kube-system',
        '--selector',
        'k8s-app=kube-dns',
        '-o',
        'json',
    ], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0])
    kube_dns_pod_name = kube_dns_pods['items'][0]['metadata']['name']
    process = subprocess.Popen([
        'kubectl',
        'port-forward',
        kube_dns_pod_name,
        '9053:53',
        '--namespace',
        'kube-system',
    ])
    time.sleep(2)
    yield
    process.terminate()

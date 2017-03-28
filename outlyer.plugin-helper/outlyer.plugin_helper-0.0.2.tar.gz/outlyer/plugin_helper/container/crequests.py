import urlparse

import requests

from outlyer.plugin_helper import container


def get(endpoint, **kwargs):
    return request('get')


def put(endpoint, **kwargs):
    return request('put')


def post(endpoint, **kwargs):
    return request('post')


def delete(endpoint, **kwargs):
    return request('delete')


def patch(endpoint, **kwargs):
    return request('patch')


def head(endpoint, **kwargs):
    return request('head')


def request(method, endpoint, **kwargs):
    endpoint = sanitize_container_endpoint(endpoint)
    return requests.request(method, endpoint, **kwargs)


def sanitize_container_endpoint(endpoint):
    if not container.is_container():
        return endpoint

    parsed = urlparse.urlparse(endpoint)
    if parsed.hostname in ['127.0.0.1', 'localhost']:
        endpoint = _set_to_container_ip(parsed)

    return endpoint


def _set_to_container_ip(parse_endpoint):
    parts = list(parse_endpoint)
    hostname = container.get_container_ip()

    if not hostname:
        hostname = parse_endpoint.hostname

    if parse_endpoint.port:
        hostname = "%s:%s" % (hostname, parse_endpoint.port)

    parts[1] = hostname

    return urlparse.urlunparse(parts)


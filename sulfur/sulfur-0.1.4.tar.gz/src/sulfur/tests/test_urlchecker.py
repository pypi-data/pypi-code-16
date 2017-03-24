import pytest

from sulfur import check_server_error, check_client_error, check_success, \
    check_2xx, check_ok, check_4xx, check_3xx, check_404, check_5xx, \
    ValidationError


@pytest.fixture
def url(port):
    return 'http://localhost:%s/base.html' % port


def test_url_checker(server, url):
    check_ok(url)
    check_success(url)
    check_2xx(url)
    with pytest.raises(ValidationError):
        check_4xx(url)
    with pytest.raises(ValidationError):
        check_3xx(url)
    with pytest.raises(ValidationError):
        check_client_error(url)
    with pytest.raises(ValidationError):
        check_server_error(url)
    check_404(server.base_url + 'does-not-exist.html')


def test_raises_on_error(url):
    with pytest.raises(ValidationError):
        check_server_error(url, raises=True)


def test_check_valid_html5(server):
    check_ok(server.base_url + 'base.html', html5=True)
    with pytest.raises(ValidationError):
        check_ok(server.base_url + 'bad.html', html5=True)
    with pytest.raises(ValidationError):
        check_ok(server.base_url + 'bad.html', html5=True)


def test_failed_post(url):
    check_5xx(url, post={'foo': 'bar'})


def test_multiple_urls(url, port):
    urls = [url, url[:-9] + 'bad.html']
    check_ok(urls)
    with pytest.raises(ValidationError):
        check_ok(urls, html5=True)

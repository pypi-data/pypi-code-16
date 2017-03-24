import pytest
from sulfur import Driver
from sulfur import errors
from sulfur.queryset import install_matches_selector_polyfill


class TestQueryset:
    @pytest.yield_fixture(scope='class')
    def driver(self, driver_type, server_url):
        from sulfur.tests.conftest import driver

        gen = driver(driver_type, server_url)
        driver = next(gen)
        driver.open('/test_queryset.html')
        yield driver
        next(gen)

    def test_fetch_queryset(self, driver):
        qs = driver.find('main p')
        assert len(qs) == 3
        assert qs.is_enabled == True
        assert qs.is_visible == True
        assert qs.is_selected == False

    def test_install_matches_selector_polyfill(self, driver):
        install_matches_selector_polyfill(driver)
        qs = driver.find('main p')
        assert qs[1].prop('className') == 'emph'
        assert qs[1].method('matches', 'p') is True
        assert qs[1].method('matches', '.emph') is True

    def test_filter_queryset(self, driver):
        qs = driver.find('main p')
        x, y, z = qs
        assert len(qs.filter('p')) == 3
        assert len(qs.filter('.emph')) == 1
        assert len(qs.filter(lambda x: x.is_visible)) == 3
        assert qs.filter([x, y, driver.elem('main')]) == [x, y]

    def test_nesting(self, driver):
        qs = driver.find('main')
        assert len(qs.find('p')) == 3



import pytest
from sulfur import Driver
from sulfur import errors


class TestElement:
    @pytest.yield_fixture(scope='class')
    def driver(self, driver_type, server_url):
        from sulfur.tests.conftest import driver

        gen = driver(driver_type, server_url)
        driver = next(gen)
        driver.open('/test_element.html')
        yield driver
        next(gen)

    def test_element_attributes(self, driver: Driver):
        h1 = driver.elem('h1')
        assert h1.id is None
        assert h1.selenium is not None
        assert h1.selenium_id is not None
        assert h1.is_visible
        assert h1.is_enabled
        assert not h1.is_selected
        assert h1.text == 'My site!'
        assert h1.tag == 'h1'

        # Position
        x, y = h1.position
        assert x < 10 and y < 10

        # Shape
        w, h = h1.shape
        assert w > h

    def test_element_fill_fails_for_non_input(self, driver):
        h1 = driver.elem('h1')

        with pytest.raises(errors.DoesNotAcceptInputError):
            h1.fill('hello world!')
        with pytest.raises(errors.DoesNotAcceptInputError):
            h1.clear()

    def test_get_element_html_properties(self, driver):
        h1 = driver.elem('h1')
        assert h1.attr('id') == ''
        assert h1.attr('class') == h1.attribute('class') == 'title'
        assert h1.prop('tagName') == h1.property('tagName') == 'H1'
        assert h1.prop('not-a-property') is None
        assert h1.css('font-size') == '32px'

    def test_set_element_html_properties(self, driver):
        h1 = driver.elem('h1')
        h1.prop(id='new_id')
        assert h1.id == 'new_id'


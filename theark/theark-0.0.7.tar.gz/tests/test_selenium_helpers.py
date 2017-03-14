import os
import unittest

from mock import patch, Mock
from the_ark import selenium_helpers

ROOT = os.path.abspath(os.path.dirname(__file__))
SELENIUM_TEST_HTML = '{0}/etc/test.html'.format(ROOT)


class SeleniumHelpersTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sh = selenium_helpers.SeleniumHelpers()
        cls.driver = cls.sh.create_driver(browserName="phantomjs")

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()

    def setUp(self):
        self.sh.load_url(SELENIUM_TEST_HTML, bypass_status_code_check=True)

    @patch("selenium.webdriver.Remote", autospec=True)
    def test_sauce_browser_valid(self, mock_sauce):
        mock_driver = Mock(spec=mock_sauce)
        mock_sauce.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(username="test", access_key="test", browserName="firefox")
        mock_sauce.assert_called_once_with(command_executor='http://test:test@ondemand.saucelabs.com:80/wd/hub',
                                           desired_capabilities={'username': 'test', 'access_key': 'test',
                                                                 'browserName': 'firefox'})

    @patch("selenium.webdriver.Remote", autospec=True)
    def test_mobile_browser_valid(self, mock_mobile):
        mock_driver = Mock(spec=mock_mobile)
        mock_mobile.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(mobile=True)
        mock_mobile.assert_called_once_with(desired_capabilities={'mobile': True})

    @patch("selenium.webdriver.Chrome", autospec=True)
    def test_chrome_browser_valid(self, mock_chrome):
        mock_driver = Mock(spec=mock_chrome)
        mock_chrome.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="chrome")
        mock_chrome.assert_called_once_with()

    @patch("selenium.webdriver.Firefox", autospec=True)
    def test_firefox_browser_valid(self, mock_firefox):
        mock_driver = Mock(spec=mock_firefox)
        mock_firefox.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="firefox")
        mock_firefox.assert_called_once_with(firefox_binary=None)

    # @patch("selenium.webdriver.Firefox", autospec=True)
    # @patch("selenium.webdriver.firefox.firefox_binary.FirefoxBinary", autospec=True)
    # def test_firefox_browser_with_binary(self, fire_binary, mock_firefox):
    #     mock_driver = Mock(spec=mock_firefox)
    #     mock_firefox.return_value = mock_driver
    #
    #     mock_binary = Mock(spec=fire_binary)
    #     fire_binary.return_value = mock_binary
    #
    #     sh = selenium_helpers.SeleniumHelpers()
    #     sh.create_driver(browserName="firefox", binary="/path/to_thing")
    #
    #     mock_firefox.assert_called_once_with(firefox_binary=mock_binary)

    @patch("selenium.webdriver.PhantomJS", autospec=True)
    def test_phantomjs_browser_valid(self, mock_phantomjs):
        mock_driver = Mock(spec=mock_phantomjs)
        mock_phantomjs.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="phantomjs")
        mock_phantomjs.assert_called_once_with()

    @patch("selenium.webdriver.PhantomJS", autospec=True)
    def test_phantomjs_browser_valid(self, mock_phantomjs):
        mock_driver = Mock(spec=mock_phantomjs)
        mock_phantomjs.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="phantomjs", binary="/path/to_thing")
        mock_phantomjs.assert_called_once_with("/path/to_thing")

    @patch("selenium.webdriver.Safari", autospec=True)
    def test_safari_browser_valid(self, mock_safari):
        mock_driver = Mock(spec=mock_safari)
        mock_safari.return_value = mock_driver
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="safari")
        mock_safari.assert_called_once_with()

    def test_no_driver_invalid(self):
        self.assertRaises(selenium_helpers.DriverAttributeError, self.sh.create_driver, browserName="browser")

    def test_driver_creation_invalid(self):
        self.assertRaises(selenium_helpers.DriverAttributeError, self.sh.create_driver, browserName="")

    def test_resize_window_valid(self):
        starting_size = self.driver.get_window_size()
        self.sh.resize_browser()
        self.assertTrue(starting_size, self.driver.get_window_size())

    @patch("selenium.webdriver.remote.webdriver.WebDriver.set_window_size")
    def test_resize_window_width_and_height_valid(self, mock_set_size):
        self.sh.resize_browser(width=50, height=50)
        self.assertTrue(mock_set_size.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.set_window_size")
    def test_resize_window_width_valid(self, mock_set_size):
        self.sh.resize_browser(width=50)
        self.assertTrue(mock_set_size.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.set_window_size")
    def test_resize_window_height_valid(self, mock_set_size):
        self.sh.resize_browser(height=50)
        self.assertTrue(mock_set_size.called)

    def test_resize_window_invalid(self):
        self.assertRaises(selenium_helpers.DriverSizeError, self.sh.resize_browser, width="text")

    def test_get_window_size_width_valid(self):
        width = self.sh.get_window_size(get_only_width=True)
        self.assertEqual(width, 400)

    def test_get_window_size_width_value_valid(self):
        window_width = self.sh.get_window_size(get_only_width=True)
        self.assertEqual(window_width, 400)

    def test_get_window_size_height_valid(self):
        height = self.sh.get_window_size(get_only_height=True)
        self.assertEqual(height, 300)

    def test_get_window_size_height_value_valid(self):
        window_height = self.sh.get_window_size(get_only_height=True)
        self.assertEqual(window_height, 300)

    def test_get_window_size_valid(self):
        width, height = self.sh.get_window_size()
        self.assertEqual(width, 400)
        self.assertEqual(height, 300)

    def test_get_window_size_value_valid(self):
        window_width, window_height = self.sh.get_window_size()
        self.assertEqual(window_width, 400)
        self.assertEqual(window_height, 300)

    def test_window_size_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.get_window_size)

    def test_add_coookie_is_valid(self):
        self.sh.add_cookie("qa", "test")
        self.assertTrue(self.driver.get_cookie("qa"), True)

    def test_add_cookie_is_false(self):
        self.sh.add_cookie("qa", "test")
        self.assertTrue(self.driver.get_cookie("no_cookie") is None)

    def test_add_cookie_expection(self):
        with self.assertRaises(selenium_helpers.DriverAttributeError):
            self.sh.add_cookie(["qa", "test"], "test")

    def test_delete_cookie_is_valid(self):
        self.sh.add_cookie("qa", "test")
        self.sh.delete_cookie("qa")
        self.assertEquals(self.driver.get_cookies(), [])

    def test_delete_cookie_expection(self):
        with self.assertRaises(selenium_helpers.DriverAttributeError):
            self.sh.delete_cookie(["qa", "test"])

    @patch("selenium.webdriver.remote.webdriver.WebDriver.get")
    def test_load_url_bypass_valid(self, mock_get):
        self.sh.load_url("www.google.com", bypass_status_code_check=True)
        self.assertTrue(mock_get.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.get")
    def test_load_url_valid(self, mock_get):
        self.sh.load_url("http://www.google.com")
        self.assertTrue(mock_get.called)

    def test_load_404_url_invalid(self):
        self.assertRaises(selenium_helpers.DriverURLError, self.sh.load_url, url="http://www.google.com/404")

    def test_load_url_invalid(self):
        self.assertRaises(selenium_helpers.DriverURLError, self.sh.load_url, url="google.com")

    def test_get_current_url_valid(self):
        test_url = "http://www.google.com/"
        self.sh.load_url(test_url)
        current_url = self.sh.get_current_url()
        self.assertEqual(current_url, test_url)

    def test_get_current_url_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverURLError, sh.get_current_url)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.refresh")
    def test_refresh_driver_valid(self, mock_refresh):
        self.sh.load_url("http://www.google.com")
        self.sh.refresh_driver()
        self.assertTrue(mock_refresh.called)

    def test_refresh_driver_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverURLError, sh.refresh_driver)

    def test_get_viewport_size_width_value_valid(self):
        viewport_width = self.sh.get_viewport_size(get_only_width=True)
        self.assertEqual(viewport_width, 400)

    def test_get_viewport_size_height_value_valid(self):
        viewport_height = self.sh.get_viewport_size(get_only_height=True)
        self.assertEqual(viewport_height, 300)

    def test_get_viewport_size_values_valid(self):
        viewport_width, viewport_height = self.sh.get_viewport_size()
        self.assertEqual(viewport_width, 400)
        self.assertEqual(viewport_height, 300)

    def test_viewport_size_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.get_viewport_size)

    def test_get_current_handle_valid(self):
        self.assertTrue(self.sh.get_window_handles(get_current=True))

    def test_get_window_handles_valid(self):
        self.assertEqual(len(self.sh.get_window_handles()), 1)

    def test_get_window_handles_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.get_window_handles)

    @patch("selenium.webdriver.remote.switch_to.SwitchTo.window")
    def test_switch_handle_specific_valid(self, mock_switch):
        current_handle = self.sh.get_window_handles(get_current=True)
        self.sh.switch_window_handle(specific_handle=current_handle)
        self.assertTrue(mock_switch.called)

    @patch("selenium.webdriver.remote.switch_to.SwitchTo.window")
    def test_switch_handle_current_valid(self, mock_switch):
        self.sh.switch_window_handle()
        self.assertTrue(mock_switch.called)

    def test_switch_handle_invalid(self):
        self.assertRaises(selenium_helpers.DriverAttributeError, self.sh.switch_window_handle, specific_handle="test")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.get_screenshot_as_base64")
    def test_get_screenshot_base64_valid(self, mock_base64):
        self.sh.get_screenshot_base64()
        self.assertTrue(mock_base64.called)

    def test_get_screehnshot_base64_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.get_screenshot_base64)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.get_screenshot_as_file")
    def test_save_screenshot_as_file_valid(self, mock_save_screenshot):
        self.sh.save_screenshot_as_file(file_path='{0}/etc/'.format(ROOT), file_name="save_screenshot_test.png")
        self.assertTrue(mock_save_screenshot.called)

    def test_save_screenshot_as_file_invalid(self):
        self.assertRaises(selenium_helpers.ScreenshotError, self.sh.save_screenshot_as_file,
                          file_path='{0}/etc/'.format(ROOT), file_name=2)

    def test_save_screenshot_as_file_unexpected_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.save_screenshot_as_file,
                          file_path='{0}/etc/'.format(ROOT), file_name="save_screenshot_test.png")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.close")
    def test_close_window_valid(self, mock_close):
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="phantomjs")
        sh.close_window()
        self.assertTrue(mock_close.called)

    def test_close_window_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.close_window)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.quit")
    def test_quit_window_valid(self, mock_quit):
        sh = selenium_helpers.SeleniumHelpers()
        sh.create_driver(browserName="phantomjs")
        sh.quit_driver()
        self.assertTrue(mock_quit.called)

    def test_quit_window_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.quit_driver)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.find_element_by_css_selector")
    def test_exist_valid(self, mock_find):
        valid_css_selector = ".valid"
        self.sh.element_exists(valid_css_selector)
        mock_find.assert_called_with(valid_css_selector)

    def test_exist_invalid(self):
        self.assertEqual(self.sh.element_exists(".invalid"), False)

    def test_visible_web_element_valid(self):
        valid_css_selector = ".valid"
        web_element = self.sh.get_element(valid_css_selector)
        self.assertTrue(self.sh.ensure_element_visible(web_element=web_element))

    def test_visible_css_valid(self):
        valid_css_selector = ".valid"
        self.assertTrue(self.sh.ensure_element_visible(valid_css_selector))

    def test_web_element_visible_invalid(self):
        web_element = self.sh.get_element(".valid")
        self.sh.hide_element(web_element=web_element)
        self.assertRaises(selenium_helpers.ElementNotVisibleError, self.sh.ensure_element_visible,
                          web_element=web_element)

    def test_visible_element_invalid(self):
        self.assertRaises(selenium_helpers.ElementError, self.sh.ensure_element_visible, css_selector=".invalid")

    def test_visible_invalid(self):
        self.assertRaises(selenium_helpers.ElementNotVisibleError, self.sh.ensure_element_visible,
                          css_selector=".hidden")

    def test_get_valid(self):
        valid_css_selector = ".valid"
        self.assertEqual(self.sh.get_element(valid_css_selector).location, {'y': 21, 'x': 48})

    def test_get_invalid(self):
        self.assertRaises(selenium_helpers.ElementError, self.sh.get_element, ".invalid")

    def test_get_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_element, "*invalid")

    def test_get_list_of_elements_valid(self):
        valid_css_selector = ".valid-list li"
        self.assertEqual(len(self.sh.get_list_of_elements(valid_css_selector)), 3)

    def test_get_list_of_elements_invalid(self):
        self.assertRaises(selenium_helpers.ElementError, self.sh.get_list_of_elements, ".invalid")

    @patch("selenium.webdriver.support.expected_conditions.presence_of_element_located")
    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_wait_valid(self, mock_wait, mock_present):
        valid_css_selector = ".valid"
        self.sh.wait_for_element(valid_css_selector)
        self.assertTrue(mock_wait.called)
        self.assertTrue(mock_present.called)

    @patch("selenium.webdriver.support.expected_conditions.visibility_of_element_located")
    @patch("selenium.webdriver.support.ui.WebDriverWait.until")
    def test_wait_visible_valid(self, mock_wait, mock_visible):
        valid_css_selector = ".valid"
        self.sh.wait_for_element(valid_css_selector, visible=True)
        self.assertTrue(mock_wait.called)
        self.assertTrue(mock_visible.called)

    def test_wait_invalid(self):
        self.assertRaises(selenium_helpers.TimeoutError, self.sh.wait_for_element, ".invalid", 1)

    @patch("selenium.webdriver.remote.webelement.WebElement.click")
    def test_click_web_element_valid(self, mock_click):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.click_an_element(web_element=web_element)
        self.assertTrue(mock_click.called)

    @patch("selenium.webdriver.remote.webelement.WebElement.click")
    def test_click_css_valid(self, mock_click):
        valid_css_selector = ".valid a"
        self.sh.click_an_element(valid_css_selector)
        self.assertTrue(mock_click.called)

    def test_click_element_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.click_an_element,
                          css_selector=".invalid a")

    def test_click_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.click_an_element, web_element="*valid a")

    def test_click_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.click_an_element, css_selector="*valid a")

    @patch("selenium.webdriver.common.action_chains.ActionChains.move_to_element_with_offset")
    def test_click_element_with_offset_web_element_valid(self, mock_click_element_with_offset):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.click_element_with_offset(web_element=web_element, x_position=30, y_position=30)
        self.assertTrue(mock_click_element_with_offset.called)

    @patch("selenium.webdriver.common.action_chains.ActionChains.move_to_element_with_offset")
    def test_click_element_with_offset_valid(self, mock_click_element_with_offset):
        valid_css_selector = ".valid a"
        self.sh.click_element_with_offset(css_selector=valid_css_selector, x_position=30, y_position=30)
        self.assertTrue(mock_click_element_with_offset.called)

    def test_click_element_with_offset_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.click_element_with_offset,
                          css_selector=".invalid a")

    def test_web_element_click_element_with_offset_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.click_element_with_offset, web_element="*invalid")

    def test_click_element_with_offset_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.click_element_with_offset, css_selector="*valid a")

    @patch("selenium.webdriver.common.action_chains.ActionChains.double_click")
    def test_double_click_web_element_valid(self, mock_double_click):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.double_click(web_element=web_element)
        self.assertTrue(mock_double_click.called)

    @patch("selenium.webdriver.common.action_chains.ActionChains.double_click")
    def test_double_click_valid(self, mock_double_click):
        valid_css_selector = ".valid a"
        self.sh.double_click(css_selector=valid_css_selector)
        self.assertTrue(mock_double_click.called)

    def test_double_click_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.double_click, css_selector=".invalid a")

    def test_web_element_double_click_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.double_click, web_element="@hidden a")

    def test_double_click_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.double_click, css_selector="@hidden a")

    @patch("selenium.webdriver.common.action_chains.ActionChains.move_by_offset")
    def test_move_cursor_to_location_valid(self, mock_move):
        self.sh.move_cursor_to_location(15, 15)
        self.assertTrue(mock_move.called)

    @patch("selenium.webdriver.common.action_chains.ActionChains.click")
    def test_move_cursor_to_location_click_valid(self, mock_click):
        self.sh.move_cursor_to_location(15, 15, click=True)
        self.assertTrue(mock_click.called)

    def test_move_cursor_to_location_invalid(self):
        self.assertRaises(selenium_helpers.CursorLocationError, self.sh.move_cursor_to_location, x_position="")

    @patch("selenium.webdriver.remote.webelement.WebElement.clear")
    def test_clear_web_element_valid(self, mock_clear):
        valid_css_selector = ".valid input"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.clear_an_element(web_element=web_element)
        self.assertTrue(mock_clear.called)

    @patch("selenium.webdriver.remote.webelement.WebElement.clear")
    def test_clear_valid(self, mock_clear):
        valid_css_selector = ".valid input"
        self.sh.clear_an_element(css_selector=valid_css_selector)
        self.assertTrue(mock_clear.called)

    def test_clear_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.clear_an_element,
                          css_selector=".invalid input")

    @patch("the_ark.selenium_helpers.SeleniumHelpers.click_an_element")
    def test_web_element_clear_unexpected_invalid(self, mock_click):
        mock_click.side_effect = Exception("Fail!")
        self.assertRaises(Exception, self.sh.clear_an_element, web_element="*invalid input")

    @patch("the_ark.selenium_helpers.SeleniumHelpers.click_an_element")
    def test_clear_unexpected_invalid(self, mock_click):
        mock_click.side_effect = Exception("Fail!")
        self.assertRaises(Exception, self.sh.clear_an_element, css_selector="*invalid input")

    @patch("selenium.webdriver.remote.webelement.WebElement.send_keys")
    def test_fill_web_element_valid(self, mock_fill):
        valid_css_selector = ".valid input"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.fill_an_element(fill_text="test text", web_element=web_element)
        self.assertTrue(mock_fill.called)

    @patch("selenium.webdriver.remote.webelement.WebElement.send_keys")
    def test_fill_valid(self, mock_fill):
        valid_css_selector = ".valid input"
        self.sh.fill_an_element(fill_text="test text", css_selector=valid_css_selector)
        self.assertTrue(mock_fill.called)

    def test_fill_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.fill_an_element, fill_text="test text",
                          css_selector=".invalid input")

    @patch("the_ark.selenium_helpers.SeleniumHelpers.clear_an_element")
    def test_fill_web_element_unexpected_invalid(self, mock_clear):
        mock_clear.side_effect = Exception("Fail!")
        self.assertRaises(Exception, self.sh.fill_an_element, fill_text="test text", web_element=".invalid &input")

    @patch("the_ark.selenium_helpers.SeleniumHelpers.clear_an_element")
    def test_fill_unexpected_invalid(self, mock_clear):
        mock_clear.side_effect = Exception("Fail!")
        self.assertRaises(Exception, self.sh.fill_an_element, fill_text="test text", css_selector=".invalid &input")

    @patch("selenium.webdriver.common.action_chains.ActionChains.send_keys")
    def test_send_special_key_valid(self, mock_keys):
        self.sh.send_special_key("tab")
        mock_keys.assert_called_once_with(u'\ue004')

    def test_send_special_key_invalid(self):
        self.assertRaises(selenium_helpers.DriverAttributeError, self.sh.send_special_key, special_key="meltmedia")

    @patch("selenium.webdriver.common.action_chains.ActionChains.move_to_element")
    def test_hover_web_element_valid(self, mock_hover):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.hover_on_element(web_element=web_element)
        self.assertTrue(mock_hover.called)

    @patch("selenium.webdriver.common.action_chains.ActionChains.move_to_element")
    def test_hover_valid(self, mock_hover):
        valid_css_selector = ".valid a"
        self.sh.hover_on_element(css_selector=valid_css_selector)
        self.assertTrue(mock_hover.called)

    def test_hover_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.hover_on_element,
                          css_selector=".invalid a")

    def test_hover_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.hover_on_element, web_element="+invalid a")

    def test_hover_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.hover_on_element, css_selector="+invalid a")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_execute_script_valid(self, mock_execute_script):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.execute_script("var element = arguments[0]; element.scrollIntoView(false);", web_element)
        self.assertTrue(mock_execute_script.called)

    def test_execute_script_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.execute_script, script="No script.")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_to_element_bottom_valid(self, mock_scroll_bottom):
        valid_css_selector = ".valid a"
        self.sh.scroll_to_element(css_selector=valid_css_selector, position_bottom=True)
        self.assertTrue(mock_scroll_bottom.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_to_element_middle_valid(self,  mock_scroll_middle):
        valid_css_selector = ".valid a"
        self.sh.scroll_to_element(css_selector=valid_css_selector, position_middle=True)
        self.assertTrue(mock_scroll_middle.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_to_web_element_top_valid(self, mock_scroll_top):
        valid_css_selector = ".valid a"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.scroll_to_element(web_element=web_element)
        self.assertTrue(mock_scroll_top.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_to_element_top_valid(self, mock_scroll_top):
        valid_css_selector = ".valid a"
        self.sh.scroll_to_element(css_selector=valid_css_selector)
        self.assertTrue(mock_scroll_top.called)

    def test_scroll_to_element_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.scroll_to_element,
                          css_selector=".invalid a")

    def test_scroll_to_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.scroll_to_element, web_element="*invalid a")

    def test_scroll_to_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.scroll_to_element, css_selector="*invalid a")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_window_to_top(self, mock_scroll_top):
        self.sh.scroll_window_to_position(scroll_top=True)
        self.assertTrue(mock_scroll_top.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_window_to_bottom(self, mock_scroll_bottom):
        self.sh.scroll_window_to_position(scroll_bottom=True)
        self.assertTrue(mock_scroll_bottom.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_window_to_position_valid(self, mock_scroll_position):
        self.sh.scroll_window_to_position(y_position=0, x_position=10)
        self.assertTrue(mock_scroll_position.called)

    def test_scroll_window_to_position_invalid(self):
        self.assertRaises(selenium_helpers.DriverAttributeError, self.sh.scroll_window_to_position,
                          y_position=None, x_position=None)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_get_window_current_scroll_position_both_valid(self, mock_scroll_both):
        self.sh.get_window_current_scroll_position(get_both_positions=True)
        mock_scroll_both.assert_any_call("return window.scrollX;")
        mock_scroll_both.assert_any_call("return window.scrollY;")

    def test_get_window_current_scroll_position_both_values_valid(self):
        x_position, y_position = self.sh.get_window_current_scroll_position(get_both_positions=True)
        self.assertEqual(x_position, 0)
        self.assertEqual(y_position, 0)

    def test_get_window_current_scroll_position_x_values_valid(self):
        x_position = self.sh.get_window_current_scroll_position(get_only_x_position=True)
        self.assertEqual(x_position, 0)

    def test_get_window_current_scroll_position_values_valid(self):
        y_position = self.sh.get_window_current_scroll_position()
        self.assertEqual(y_position, 0)

    def test_get_window_current_scroll_position_invalid(self):
        sh = selenium_helpers.SeleniumHelpers()
        self.assertRaises(selenium_helpers.DriverAttributeError, sh.get_window_current_scroll_position)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_web_element_top_valid(self, mock_scroll_element_top):
        valid_css_selector = ".scrollable"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.scroll_an_element(web_element=web_element, scroll_top=True)
        self.assertTrue(mock_scroll_element_top.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_top_valid(self, mock_scroll_element_top):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_top=True)
        self.assertTrue(mock_scroll_element_top.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_bottom_valid(self, mock_scroll_element_bottom):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_bottom=True)
        self.assertTrue(mock_scroll_element_bottom.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_horizontal_valid(self, mock_scroll_element_horizontal):
        valid_css_selector = ".image-scroll"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_horizontal=True)
        self.assertTrue(mock_scroll_element_horizontal.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_left_valid(self, mock_scroll_element_horizontal):
        valid_css_selector = ".image-scroll"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_left=True)
        self.assertTrue(mock_scroll_element_horizontal.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_right_valid(self, mock_scroll_element_horizontal):
        valid_css_selector = ".image-scroll"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_right=True)
        self.assertTrue(mock_scroll_element_horizontal.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_y_position_valid(self, mock_scroll_element_vertical):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector, y_position=50)
        self.assertTrue(mock_scroll_element_vertical.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_x_position_valid(self, mock_scroll_element_horizontal):
        valid_css_selector = ".image-scroll"
        self.sh.scroll_an_element(css_selector=valid_css_selector, x_position=50)
        self.assertTrue(mock_scroll_element_horizontal.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_scroll_element_valid(self, mock_scroll_element_padding):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_padding=5)
        self.assertTrue(mock_scroll_element_padding.called)

    def test_scroll_element_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.scroll_an_element,
                          css_selector=".not-scrollable")

    def test_scroll_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.scroll_an_element, web_element="!not-scrollable")

    def test_scroll_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.scroll_an_element, css_selector="!not-scrollable")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_get_web_element_current_scroll_position_scripts_valid(self, mock_element_scroll):
        valid_css_selector = ".scrollable"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.get_element_current_scroll_position(web_element=web_element)
        mock_element_scroll.assert_any_call("var element = arguments[0]; "
                                            "scrollPosition = element.scrollLeft; "
                                            "return scrollPosition;", web_element)
        mock_element_scroll.assert_any_call("var element = arguments[0]; "
                                            "scrollPosition = element.scrollTop; "
                                            "return scrollPosition;", web_element)

    def test_get_web_element_current_scroll_position_both_valid(self):
        valid_css_selector = ".scrollable"
        web_element = self.sh.get_element(valid_css_selector)
        x_pos, y_pos = self.sh.get_element_current_scroll_position(web_element=web_element, get_both_positions=True)
        self.assertEqual(x_pos, 0)
        self.assertEqual(y_pos, 0)

    def test_get_element_current_scroll_position_x_valid(self):
        valid_css_selector = ".scrollable"
        self.assertEqual(self.sh.get_element_current_scroll_position(css_selector=valid_css_selector,
                                                                     get_only_x_position=True), 0)

    def test_get_element_current_scroll_position_valid(self):
        valid_css_selector = ".scrollable"
        self.assertEqual(self.sh.get_element_current_scroll_position(css_selector=valid_css_selector), 0)

    def test_get_element_current_scroll_position_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.get_element_current_scroll_position,
                          css_selector=".not-scrollable")

    def test_get_web_element_current_scroll_position_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_element_current_scroll_position, web_element="*not-scrollable")

    def test_get_element_current_scroll_position_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_element_current_scroll_position, css_selector="*not-scrollable")

    def test_is_web_element_scroll_position_at_top_true_valid(self):
        valid_css_selector = ".scrollable"
        web_element = self.sh.get_element(valid_css_selector)
        self.assertTrue(self.sh.get_is_element_scroll_position_at_top(web_element=web_element))

    def test_is_element_scroll_position_at_top_true_valid(self):
        valid_css_selector = ".scrollable"
        self.assertTrue(self.sh.get_is_element_scroll_position_at_top(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_top_false_valid(self):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector)
        self.assertFalse(self.sh.get_is_element_scroll_position_at_top(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_top_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.get_is_element_scroll_position_at_top,
                          css_selector=".not-scrollable")

    def test_is_web_element_scroll_position_at_top_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_top, web_element="*not-scrollable")

    def test_is_element_scroll_position_at_top_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_top, css_selector="*not-scrollable")

    def test_is_web_element_scroll_position_at_bottom_true_valid(self):
        valid_css_selector = ".scrollable"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.scroll_an_element(web_element=web_element, scroll_bottom=True)
        self.assertTrue(self.sh.get_is_element_scroll_position_at_bottom(web_element=web_element))

    def test_is_element_scroll_position_at_bottom_true_valid(self):
        valid_css_selector = ".scrollable"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_bottom=True)
        self.assertTrue(self.sh.get_is_element_scroll_position_at_bottom(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_bottom_false_valid(self):
        valid_css_selector = ".scrollable"
        self.assertFalse(self.sh.get_is_element_scroll_position_at_bottom(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_bottom_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.get_is_element_scroll_position_at_bottom,
                          css_selector=".not-scrollable")

    def test_is_web_element_scroll_position_at_bottom_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_bottom, web_element="*not-scrollable")

    def test_is_element_scroll_position_at_bottom_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_bottom, css_selector="*not-scrollable")

    def test_is_web_element_scroll_position_at_most_right_true_valid(self):
        valid_css_selector = ".image-scroll"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.scroll_an_element(web_element=web_element, scroll_right=True)
        self.assertTrue(self.sh.get_is_element_scroll_position_at_most_right(web_element=web_element))

    def test_is_element_scroll_position_at_most_right_true_valid(self):
        valid_css_selector = ".image-scroll"
        self.sh.scroll_an_element(css_selector=valid_css_selector, scroll_right=True)
        self.assertTrue(self.sh.get_is_element_scroll_position_at_most_right(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_most_right_false_valid(self):
        valid_css_selector = ".image-scroll"
        self.assertFalse(self.sh.get_is_element_scroll_position_at_most_right(css_selector=valid_css_selector))

    def test_is_element_scroll_position_at_most_right_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions,
                          self.sh.get_is_element_scroll_position_at_most_right,
                          css_selector=".not-scrollable")

    def test_is_web_element_scroll_position_at_most_right_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_most_right,
                          web_element="*not-scrollable")

    def test_is_element_scroll_position_at_most_right_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.get_is_element_scroll_position_at_most_right,
                          css_selector="*not-scrollable")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_hide_web_element_valid(self, mock_hide):
        valid_css_selector = ".valid"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.hide_element(web_element=web_element)
        self.assertTrue(mock_hide.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_hide_element_valid(self, mock_hide):
        valid_css_selector = ".valid"
        self.sh.hide_element(css_selector=valid_css_selector)
        self.assertTrue(mock_hide.called)

    def test_hide_element_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.hide_element, css_selector=".invalid")

    def test_hide_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.hide_element, web_element="*invalid")

    def test_hide_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.hide_element, css_selector="*invalid")

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_show_web_element_valid(self, mock_show):
        valid_css_selector = ".valid"
        web_element = self.sh.get_element(valid_css_selector)
        self.sh.show_element(web_element=web_element)
        self.assertTrue(mock_show.called)

    @patch("selenium.webdriver.remote.webdriver.WebDriver.execute_script")
    def test_show_element_valid(self, mock_show):
        valid_css_selector = ".valid"
        self.sh.show_element(css_selector=valid_css_selector)
        self.assertTrue(mock_show.called)

    def test_show_element_invalid(self):
        self.assertRaises(selenium_helpers.SeleniumHelperExceptions, self.sh.show_element, css_selector=".invalid")

    def test_show_web_element_unexpected_invalid(self):
        self.assertRaises(Exception, self.sh.show_element, web_element="*invalid_element")

    @patch("the_ark.selenium_helpers.SeleniumHelpers.get_element")
    def test_show_element_unexpected_invalid(self, mock_get):
        mock_get.side_effect = Exception("Boo!")
        self.assertRaises(Exception, self.sh.show_element, css_selector="*invalid_selector")

    def test_selenium_exception_to_string_with_details(self):
        selenium_exception = selenium_helpers.SeleniumHelperExceptions("message",
                                                                       "stacktrace:\nLine 1\nLine 2",
                                                                       "google")
        error_string = selenium_exception.__str__()
        self.assertIn("current_url", error_string)

    def test_driver_exception_to_string_without_details(self):
        driver_exception = selenium_helpers.DriverExceptions("Message text")
        error_string = driver_exception.__str__()
        self.assertNotIn("stacktrace", error_string)

    def test_driver_exception_to_string_with_details(self):
        driver_exception = selenium_helpers.DriverExceptions("message", "stacktrace:\nLine 1\nLine 2")
        error_string = driver_exception.__str__()
        self.assertIn("stacktrace", error_string)

    def test_field_handler_exception_to_string_with_details(self):
        field_handler = selenium_helpers.DriverExceptions("message",
                                                          "stacktrace:\nLine 1\nLine 2",
                                                          {"desired_url": "http://www.google.com"})
        error_string = field_handler.__str__()
        self.assertIn("desired_url", error_string)
        self.assertIn("stacktrace", error_string)

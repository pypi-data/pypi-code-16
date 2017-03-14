import unittest

from the_ark.actions import Actions, ActionException
from the_ark.field_handlers import STRING_FIELD, EMAIL_FIELD, PHONE_FIELD, ZIP_CODE_FIELD, DATE_FIELD
from the_ark.resources.action_constants import *
from the_ark.selenium_helpers import SeleniumHelpers, SeleniumHelperExceptions
from mock import patch


class ActionTestCase(unittest.TestCase):
    def setUp(self):
        self.instantiate_screenshot_class()

    @patch("the_ark.selenium_helpers.SeleniumHelpers")
    def instantiate_screenshot_class(self, selenium_helper):
        self.ac = Actions(selenium_helper)

    # - Dispatch Methods
    @patch("the_ark.actions.Actions.dispatch_action")
    def test_dispatch_list(self, mock_dispatch):
        action_list = ["pickles", "pineapples"]
        self.ac.dispatch_list_of_actions(action_list)
        mock_dispatch.return_value = True
        self.assertEqual(len(mock_dispatch.mock_calls), 2)
        mock_dispatch.assert_called_with(action_list[1], None)

    @patch("the_ark.actions.Actions.dispatch_action")
    def test_dispatch_list_without_list(self, mock_dispatch):
        action_list = False
        with self.assertRaises(ActionException) as type_error:
            self.ac.dispatch_list_of_actions(action_list)
        self.assertIn("list type", type_error.exception.msg)

    @patch("the_ark.actions.Actions.load_url")
    def test_dispatch_action(self, mock_load):
        action = {ACTION_KEY: LOAD_URL_ACTION}
        mock_load.return_value = True
        self.ac.dispatch_action(action)
        mock_load.assert_called_with(action, None)

    @patch("the_ark.actions.Actions.load_url")
    def test_dipatch_action_selenium_error(self, mock_load):
        action = {ACTION_KEY: LOAD_URL_ACTION}
        mock_load.side_effect = SeleniumHelperExceptions("Boom!", "stacktrace", "www.meltmedia.com")
        with self.assertRaises(ActionException) as selenium_error:
            self.ac.dispatch_action(action)

        self.assertIn("www.meltmedia.com", selenium_error.exception.msg)

    @patch("the_ark.actions.Actions.load_url")
    def test_dipatch_action_key_error(self, mock_load):
        action = {ACTION_KEY: LOAD_URL_ACTION}
        mock_load.side_effect = KeyError("Boom!")
        with self.assertRaises(ActionException) as key_error:
            self.ac.dispatch_action(action)

        self.assertIn("key named 'Boom!'", key_error.exception.msg)

    @patch("the_ark.actions.Actions.load_url")
    def test_dipatch_action_attribute_error(self, mock_load):
        action = {ACTION_KEY: LOAD_URL_ACTION}
        mock_load.side_effect = AttributeError("Boom!")
        with self.assertRaises(ActionException) as attr_error:
            self.ac.dispatch_action(action)

        self.assertIn("AttributeError", attr_error.exception.msg)

    @patch("the_ark.actions.Actions.load_url")
    def test_dipatch_action_general_error(self, mock_load):
        action = {ACTION_KEY: LOAD_URL_ACTION}
        mock_load.side_effect = Exception("Boom!")
        with self.assertRaises(ActionException) as e:
            self.ac.dispatch_action(action)

        self.assertIn("error", e.exception.msg)

    # - Load URL Action
    @patch("the_ark.selenium_helpers.SeleniumHelpers.load_url")
    @patch("the_ark.selenium_helpers.SeleniumHelpers.get_current_url")
    def test_load_url_action_with_just_path(self, mock_url, sh_load):
        sh = SeleniumHelpers()
        ac = Actions(sh)

        action = {
            ACTION_KEY: LOAD_URL_ACTION,
            PATH_KEY: "/pickles"
        }

        test_url = "http://www.meltmedia.com"
        mock_url.return_value = test_url
        ac.load_url(action)
        sh_load.assert_called_with(test_url + "/pickles", None)

    @patch("the_ark.selenium_helpers.SeleniumHelpers.load_url")
    def test_load_url_action_with_url_and_path(self, sh_load):
        sh = SeleniumHelpers()
        ac = Actions(sh)
        test_url = "http://www.meltmedia.com"
        action = {
            ACTION_KEY: LOAD_URL_ACTION,
            PATH_KEY: "/pickles",
            URL_KEY: test_url
        }
        ac.load_url(action)
        sh_load.assert_called_with(test_url + "/pickles", None)

    @patch("the_ark.selenium_helpers.SeleniumHelpers.load_url")
    def test_load_url_action_with_just_url_withbypass(self, sh_load):
        sh = SeleniumHelpers()
        ac = Actions(sh)
        test_url = "http://www.meltmedia.com"
        action = {
            ACTION_KEY: LOAD_URL_ACTION,
            URL_KEY: test_url,
            BYPASS_404_KEY: True
        }
        ac.load_url(action)
        sh_load.assert_called_with(test_url, True)

    # - Click Action
    def test_click(self):
        action = {
            ACTION_KEY: CLICK_ACTION,
            CSS_SELECTOR_KEY: ".pickles"
        }
        self.ac.click(action, None)

        self.ac.sh.click_an_element.assert_called_with(action[CSS_SELECTOR_KEY])

    def test_click_with_element(self):
        action = {
            ACTION_KEY: CLICK_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.click(action, element)

        self.ac.sh.click_an_element.assert_called_with(web_element=element)

    # - Hover Action
    def test_hover(self):
        action = {
            ACTION_KEY: HOVER_ACTION,
            CSS_SELECTOR_KEY: ".pickles"
        }
        self.ac.hover(action, None)

        self.ac.sh.hover_on_element.assert_called_with(action[CSS_SELECTOR_KEY])

    def test_hover_with_element(self):
        action = {
            ACTION_KEY: HOVER_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.hover(action, element)

        self.ac.sh.hover_on_element.assert_called_with(web_element=element)

    # - Enter Text Action
    def test_enter_text(self):
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_KEY: "input text"
        }
        self.ac.enter_text(action, None)

        self.ac.sh.fill_an_element.assert_called_with(action[INPUT_KEY], action[CSS_SELECTOR_KEY])

    def test_enter_text_with_element(self):
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            ELEMENT_KEY: True,
            INPUT_KEY: "input text"
        }
        element = "element"
        self.ac.enter_text(action, element)

        self.ac.sh.fill_an_element.assert_called_with(action[INPUT_KEY], web_element=element)

    @patch('the_ark.input_generator.generate_string')
    def test_enter_text_as_string_with_element(self, mock_string):
        test_string = "Test String"
        mock_string.return_value = test_string
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            ELEMENT_KEY: True,
            INPUT_TYPE_KEY: STRING_FIELD
        }
        element = "element"
        self.ac.enter_text(action, element)

        self.ac.sh.fill_an_element.assert_called_with(test_string, web_element=element)

    @patch('the_ark.input_generator.generate_email')
    def test_enter_text_as_email(self, mock_email):
        test_email = "testingStuff@meltmedia.com"
        mock_email.return_value = test_email
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_TYPE_KEY: EMAIL_FIELD
        }
        self.ac.enter_text(action, None)

        self.ac.sh.fill_an_element.assert_called_with(test_email, action[CSS_SELECTOR_KEY])

    @patch('the_ark.input_generator.generate_zip_code')
    def test_enter_text_as_zip_code(self, mock_zip):
        test_zip = "12345"
        mock_zip.return_value = test_zip
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_TYPE_KEY: ZIP_CODE_FIELD
        }
        self.ac.enter_text(action, None)

        self.ac.sh.fill_an_element.assert_called_with(test_zip, action[CSS_SELECTOR_KEY])

    @patch('the_ark.input_generator.generate_phone')
    def test_enter_text_as_phone_number(self, mock_phone):
        test_phone = "5557891011"
        mock_phone.return_value = test_phone
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_TYPE_KEY: PHONE_FIELD
        }
        self.ac.enter_text(action, None)

        self.ac.sh.fill_an_element.assert_called_with(test_phone, action[CSS_SELECTOR_KEY])

    @patch('the_ark.input_generator.generate_date')
    def test_enter_text_as_date(self, mock_date):
        test_date = "01/27/1987"
        mock_date.return_value = test_date
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_TYPE_KEY: DATE_FIELD
        }
        self.ac.enter_text(action, None)

        self.ac.sh.fill_an_element.assert_called_with(test_date, action[CSS_SELECTOR_KEY])

    @patch('the_ark.input_generator.generate_date')
    def test_enter_text_as_unknown_type(self, mock_date):
        test_date = "01/27/1987"
        mock_date.return_value = test_date
        action = {
            ACTION_KEY: ENTER_TEXT_ACTION,
            CSS_SELECTOR_KEY: ".enter",
            INPUT_TYPE_KEY: "Pickles"
        }

        with self.assertRaises(ActionException) as unknown_input_type:
            self.ac.enter_text(action, None)

        self.assertIn(action[INPUT_TYPE_KEY], unknown_input_type.exception.msg)

    # - Scroll Actions
    def test_scroll_window_to_position(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_POSITION_ACTION,
            POSITION_TOP_KEY: "1",
            POSITION_BOTTOM_KEY: "2",
            X_POSITION_KEY: 300,
            Y_POSITION_KEY: 4000
        }

        self.ac.scroll_window_to_position(action, None)

        self.ac.sh.scroll_window_to_position.assert_called_with(action[Y_POSITION_KEY], action[X_POSITION_KEY],
                                                                action[POSITION_TOP_KEY], action[POSITION_BOTTOM_KEY])

    def test_scroll_window_to_position_with_defaults(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_POSITION_ACTION,
            POSITION_TOP_KEY: "1",
            X_POSITION_KEY: 300,
        }

        self.ac.scroll_window_to_position(action)

        self.ac.sh.scroll_window_to_position.assert_called_with(0, action[X_POSITION_KEY],
                                                                action[POSITION_TOP_KEY], 0)

    def test_scroll_window_to_element_defaults(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".scroll"
        }
        self.ac.scroll_window_to_element(action, None)

        self.ac.sh.scroll_to_element.assert_called_with(action[CSS_SELECTOR_KEY], position_bottom=None,
                                                        position_middle=None)

    def test_scroll_window_to_element_with_top_and_bottom(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".scroll",
            POSITION_BOTTOM_KEY: True,
            POSITION_MIDDLE_KEY: True
        }
        self.ac.scroll_window_to_element(action, None)

        self.ac.sh.scroll_to_element.assert_called_with(action[CSS_SELECTOR_KEY], position_bottom=True,
                                                        position_middle=True)

    def test_scroll_window_to_element_with_element(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_ELEMENT_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.scroll_window_to_element(action, element)

        self.ac.sh.scroll_to_element.assert_called_with(web_element=element, position_bottom=None,
                                                        position_middle=None)

    def test_scroll_window_to_element_with_element_and_top_and_bottom(self):
        action = {
            ACTION_KEY: SCROLL_WINDOW_TO_ELEMENT_ACTION,
            ELEMENT_KEY: True,
            POSITION_BOTTOM_KEY: True,
            POSITION_MIDDLE_KEY: True
        }
        element = "element"
        self.ac.scroll_window_to_element(action, element)

        self.ac.sh.scroll_to_element.assert_called_with(position_bottom=True, position_middle=True,
                                                        web_element=element)

    def test_scroll_an_element_defaults(self):
        action = {
            ACTION_KEY: SCROLL_AN_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".scrollable"
        }
        self.ac.scroll_an_element(action, None)

        self.ac.sh.scroll_an_element.assert_called_with(css_selector=action[CSS_SELECTOR_KEY], scroll_bottom=None,
                                                        scroll_padding=None, scroll_top=None, x_position=None,
                                                        y_position=None)

    def test_scroll_an_element_with_values(self):
        action = {
            ACTION_KEY: SCROLL_AN_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".scrollable",
            POSITION_BOTTOM_KEY: True,
            X_POSITION_KEY: 100,
            Y_POSITION_KEY: 1200,
            SCROLL_PADDING_KEY: 45,
            POSITION_TOP_KEY: False
        }
        self.ac.scroll_an_element(action, None)

        self.ac.sh.scroll_an_element.assert_called_with(css_selector=action[CSS_SELECTOR_KEY],
                                                        scroll_bottom=action[POSITION_BOTTOM_KEY],
                                                        scroll_padding=action[SCROLL_PADDING_KEY],
                                                        scroll_top=action[POSITION_TOP_KEY],
                                                        x_position=action[X_POSITION_KEY],
                                                        y_position=action[Y_POSITION_KEY])

    def test_scroll_an_element_with_element_and_defaults(self):
        action = {
            ACTION_KEY: SCROLL_AN_ELEMENT_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.scroll_an_element(action, element)

        self.ac.sh.scroll_an_element.assert_called_with(web_element=element, scroll_bottom=None, scroll_padding=None,
                                                        scroll_top=None, x_position=None, y_position=None)

    def test_scroll_an_element_With_element_and_values(self):
        action = {
            ACTION_KEY: SCROLL_AN_ELEMENT_ACTION,
            ELEMENT_KEY: True,
            POSITION_BOTTOM_KEY: True,
            X_POSITION_KEY: 100,
            Y_POSITION_KEY: 1200,
            SCROLL_PADDING_KEY: 45,
            POSITION_TOP_KEY: False
        }
        element = "element"
        self.ac.scroll_an_element(action, element)

        self.ac.sh.scroll_an_element.assert_called_with(web_element=element, scroll_bottom=action[POSITION_BOTTOM_KEY],
                                                        scroll_padding=action[SCROLL_PADDING_KEY],
                                                        scroll_top=action[POSITION_TOP_KEY],
                                                        x_position=action[X_POSITION_KEY],
                                                        y_position=action[Y_POSITION_KEY])

    # - Refresh Action
    def test_refresh(self):
        self.ac.refresh("action")
        self.ac.sh.refresh.called_once()

    # - Sleep Action
    @patch('time.sleep')
    def test_sleep(self, mock_sleep):
        action = {
            ACTION_KEY: SLEEP_ACTION,
            DURATION_KEY: 10
        }
        self.ac.sleep(action)
        mock_sleep.assert_called_with(action[DURATION_KEY])

    # - Wait for Element Action
    def test_wait_for_element_defaults(self):
        action = {
            ACTION_KEY: WAIT_FOR_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".wait"
        }
        self.ac.wait_for_element(action)
        self.ac.sh.wait_for_element.assert_called_with(action[CSS_SELECTOR_KEY], 15)

    def test_wait_for_element_with_duration(self):
        action = {
            ACTION_KEY: WAIT_FOR_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".wait",
            DURATION_KEY: 10
        }
        self.ac.wait_for_element(action)
        self.ac.sh.wait_for_element.assert_called_with(action[CSS_SELECTOR_KEY], action[DURATION_KEY])

    # - Special Key Action
    def test_send_special_key(self):
        action = {
            ACTION_KEY: SEND_SPECIAL_KEY_ACTION,
            SPECIAL_KEY_KEY: "ENTER"
        }
        self.ac.send_special_key(action)
        self.ac.sh.send_special_key.assert_called_with(action[SPECIAL_KEY_KEY])

    # - Show Element Action
    def test_show_element(self):
        action = {
            ACTION_KEY: SHOW_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".pickles"
        }
        self.ac.show_element(action, None)

        self.ac.sh.show_element.assert_called_with(action[CSS_SELECTOR_KEY])

    def test_show_element_with_element(self):
        action = {
            ACTION_KEY: SHOW_ELEMENT_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.show_element(action, element)

        self.ac.sh.show_element.assert_called_with(web_element=element)

    # - Hide Element Action
    def test_hide_element(self):
        action = {
            ACTION_KEY: HIDE_ELEMENT_ACTION,
            CSS_SELECTOR_KEY: ".pickles"
        }
        self.ac.hide_element(action, None)

        self.ac.sh.hide_element.assert_called_with(action[CSS_SELECTOR_KEY])

    def test_hide_element_with_element(self):
        action = {
            ACTION_KEY: HIDE_ELEMENT_ACTION,
            ELEMENT_KEY: True
        }
        element = "element"
        self.ac.hide_element(action, element)

        self.ac.sh.hide_element.assert_called_with(web_element=element)

    # - Execute Script Action
    def test_execute_script(self):
        action = {
            ACTION_KEY: EXECUTE_SCRIPT_ACTION,
            SCRIPT_KEY: "script text"
        }
        self.ac.execute_script(action, None)

        self.ac.sh.execute_script.assert_called_with(action[SCRIPT_KEY])

    def test_execute_script_with_element(self):
        action = {
            ACTION_KEY: EXECUTE_SCRIPT_ACTION,
            ELEMENT_KEY: True,
            SCRIPT_KEY: "script text"
        }
        element = "element"
        self.ac.execute_script(action, element)

        self.ac.sh.execute_script.assert_called_with(action[SCRIPT_KEY], element)

    # - Switch Window Handle Action
    def test_switch_window_handle(self):
        action = {
            ACTION_KEY: "switch_window_handle"
        }
        self.ac.switch_window_handle(action)
        self.ac.sh.switch_window_handle.assert_called_with()

    def test_switch_window_handle_with_index(self):
        fake_handles = ["handle1", "handle2"]
        action = {
            ACTION_KEY: "switch_window_handle",
            INDEX_KEY: 1
        }
        self.ac.sh.get_window_handles.return_value = fake_handles
        self.ac.switch_window_handle(action)
        self.ac.sh.switch_window_handle.assert_called_with(fake_handles[action[INDEX_KEY]])

    # - Close Window Action
    def test_close_window(self):
        action = {
            ACTION_KEY: CLOSE_WINDOW_ACTION
        }
        self.ac.close_window(action)
        self.ac.sh.close_window.assert_called_with()

    # - For Each Action
    @patch('the_ark.actions.Actions.dispatch_list_of_actions')
    def test_for_each(self, mock_dispatch):
        action ={
            ACTION_KEY: FOR_EACH_ACTION,
            CSS_SELECTOR_KEY: ".for-each",
            ALLOW_EMPTY_KEY: False,
            ACTION_LIST_KEY: [
                {
                    ACTION_KEY: CLICK_ACTION,
                    ELEMENT_KEY: True
                },
            ]
        }
        self.ac.sh.element_exists.return_value = True
        self.ac.sh.get_list_of_elements.return_value = ["element1", "element2"]

        self.ac.for_each(action)

        self.assertEqual(len(mock_dispatch.mock_calls), 2)

    @patch('the_ark.actions.Actions.dispatch_list_of_actions')
    def test_for_each_without_elements(self, mock_dispatch):
        action = {
            ACTION_KEY: FOR_EACH_ACTION,
            CSS_SELECTOR_KEY: ".for-each",
            ALLOW_EMPTY_KEY: False,
            ACTION_LIST_KEY: [
                {
                    ACTION_KEY: CLICK_ACTION,
                    ELEMENT_KEY: True
                },
            ]
        }
        self.ac.sh.element_exists.return_value = False

        with self.assertRaises(ActionException) as type_error:
            self.ac.for_each(action)

        self.assertIn("no elements", type_error.exception.msg)

    @patch('the_ark.actions.Actions.dispatch_list_of_actions')
    def test_for_each_child(self, mock_dispatch):
        action = {
            ACTION_KEY: FOR_EACH_ACTION,
            CSS_SELECTOR_KEY: ".for-each",
            ALLOW_EMPTY_KEY: False,
            CHILD_KEY: True,
            ACTION_LIST_KEY: [
                {
                    ACTION_KEY: CLICK_ACTION,
                    ELEMENT_KEY: True
                },
            ]
        }
        self.ac.sh.element_exists.return_value = ["element1", "element2"]
        self.ac.for_each(action)

    @patch('the_ark.actions.Actions.dispatch_list_of_actions')
    def test_for_each_allow_empty(self, mock_dispatch):
        action = {
            ACTION_KEY: FOR_EACH_ACTION,
            CSS_SELECTOR_KEY: ".for-each",
            ALLOW_EMPTY_KEY: True,
            ACTION_LIST_KEY: [
                {
                    ACTION_KEY: CLICK_ACTION,
                    ELEMENT_KEY: True
                },
            ]
        }
        self.ac.sh.element_exists.return_value = False
        self.ac.for_each(action)

    @patch('the_ark.actions.Actions.dispatch_list_of_actions')
    def test_for_each_do_not_increment(self, mock_dispatch):
        action = {
            ACTION_KEY: FOR_EACH_ACTION,
            CSS_SELECTOR_KEY: ".for-each",
            ALLOW_EMPTY_KEY: True,
            DO_NOT_INCREMENT_KEY: True,
            ACTION_LIST_KEY: [
                {
                    ACTION_KEY: CLICK_ACTION,
                    ELEMENT_KEY: True
                },
            ]
        }
        self.ac.sh.element_exists.return_value = True
        self.ac.sh.get_list_of_elements.return_value = ["element1", "element2"]
        self.ac.for_each(action)

    # - ActionException
    def test_exception_text(self):
        ac = ActionException("test")
        self.assertIn("test", str(ac))

    def test_exception_with_stacktrace(self):
        ac = ActionException("test", "stacktrace testing")
        self.assertIn("stacktrace testing", str(ac))

    def test_exception_with_details(self):
        ac = ActionException("test", details={"meltQA": "Rocks"})
        self.assertIn("Rocks", str(ac))
        self.assertIn("Exception Details", str(ac))


import unittest
from the_ark.field_handlers import FieldHandler, FieldHandlerException, SeleniumError, MissingKey, UnknownFieldType
from the_ark import selenium_helpers
from mock import patch


class FieldHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.instantiate_field_handler()

    @patch("the_ark.selenium_helpers.SeleniumHelpers")
    def instantiate_field_handler(self, selenium_helper):
        fake_driver = "driver"
        self.sh = selenium_helper(fake_driver)
        self.fh = FieldHandler(self.sh)

    # ===================================================================
    # --- dispatch_field() tests
    # ===================================================================
    # - Text Field
    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_text_field_without_confirm(self, text_method):
        field_data = {
            "type": "STRING",
            "css_selector": "#field",
            "input": "text"
        }
        text_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        text_method.assert_called_once_with(field_data["css_selector"], field_data["input"], None)

    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_text_field_with_confirm(self, text_method):
        field_data = {
            "type": "EMAIL",
            "css_selector": "#field",
            "input": "text",
            "confirm_css_selector": "#confirm-field"
        }
        text_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        text_method.assert_called_once_with(field_data["css_selector"],
                                            field_data["input"],
                                            field_data["confirm_css_selector"])

    # - Check Box Field
    @patch("the_ark.field_handlers.FieldHandler.handle_check_box")
    def test_dispatch_check_box_field(self, check_box_method):
        field_data = {
            "type": "CHECK_BOX",
            "enum": [{"#agree": "Agree"}, {"#disagree": "Disagree"}],
            "input": [1]
        }
        check_box_method.return_value = "text"
        self.sh.fill_an_element.return_value = "text"
        self.fh.dispatch_field(field_data)
        check_box_method.assert_called_once_with(field_data["enum"], field_data["input"])

    # - Radio Button Field
    @patch("the_ark.field_handlers.FieldHandler.handle_radio_button")
    def test_dispatch_radio_button_field(self, radio_button_method):
        field_data = {
            "type": "RADIO",
            "enum": [{"#agree": "Agree"}, {"#disagree": "Disagree"}],
            "input": 1
        }
        radio_button_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        radio_button_method.assert_called_once_with(field_data["enum"], field_data["input"])

    # - Select Field
    @patch("the_ark.field_handlers.FieldHandler.handle_select")
    def test_dispatch_select_field_without_first_valid(self, select_method):
        field_data = {
            "type": "SELECT",
            "css_selector": "#state",
            "enum": ["Agree", "Disagree"],
            "input": 1
        }
        select_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        select_method.assert_called_once_with(field_data["css_selector"], field_data["input"], False)

    @patch("the_ark.field_handlers.FieldHandler.handle_select")
    def test_dispatch_select_field_with_first_valid_as_true(self, select_method):
        field_data = {
            "type": "SELECT",
            "css_selector": "#state",
            "enum": ["Agree", "Disagree"],
            "input": 30,
            "first_valid": True
        }
        select_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        select_method.assert_called_once_with(field_data["css_selector"],
                                              field_data["input"],
                                              field_data["first_valid"])

    @patch("the_ark.field_handlers.FieldHandler.handle_select")
    def test_dispatch_select_field_with_first_valid_as_false(self, select_method):
        field_data = {
            "type": "SELECT",
            "css_selector": "#state",
            "enum": ["Agree", "Disagree"],
            "input": 30,
            "first_valid": False
        }
        select_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        select_method.assert_called_once_with(field_data["css_selector"],
                                              field_data["input"],
                                              field_data["first_valid"])

    # - Drop Down Field
    @patch("the_ark.field_handlers.FieldHandler.handle_drop_down")
    def test_dispatch_drop_down_field(self, drop_down_method):
        field_data = {
            "type": "DROP_DOWN",
            "css_selector": "#food",
            "enum": [{"#pizza": "Pizza"}, {"#applesauce": "Applesauce"}],
            "input": [0, 1]
        }
        drop_down_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        drop_down_method.assert_called_once_with(field_data["css_selector"], field_data["enum"], field_data["input"])

    # - Button Field
    @patch("the_ark.field_handlers.FieldHandler.handle_button")
    def test_dispatch_button_field(self, button_method):
        field_data = {
            "type": "BUTTON",
            "css_selector": "#food"
        }
        button_method.return_value = "text"
        self.fh.dispatch_field(field_data)
        button_method.assert_called_once_with(field_data["css_selector"])

    # - Exceptions
    # Unknown Type
    def test_dispatch_with_unknown_field_type(self):
        field_data = {
            "type": "Unavailable",
        }
        with self.assertRaises(UnknownFieldType) as error_message:
            self.fh.dispatch_field(field_data)
        # Check that the else statement is called by verifying the exception text contains the word "unknown"
        self.assertIn(field_data["type"], error_message.exception.msg)

    # FieldHandlerException()
    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_field_handler_exception_without_name(self, text_method):
        field_data = {
            "type": "STRING",
            "css_selector": "#field",
            "input": "text"
        }
        text_method.side_effect = FieldHandlerException("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertNotIn("named", error_message.exception.msg)

    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_field_handler_exception_with_name(self, text_method):
        field_data = {
            "type": "STRING",
            "css_selector": "#field",
            "input": "text",
            "name": "First Name"
        }
        text_method.side_effect = FieldHandlerException("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertIn(field_data["name"], error_message.exception.msg)

    # KeyError()
    def test_dispatch_key_error_without_name(self):
        field_data = {
            "css_selector": "#field",
            "input": "text",
        }
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertEquals("'type'", error_message.exception.details["missing_key"])
        self.assertNotIn("named", error_message.exception.msg)

    def test_dispatch_key_error_with_name(self):
        field_data = {
            "css_selector": "#field",
            "input": "text",
            "name": "First Name"
        }
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertIn(field_data["name"], error_message.exception.msg)
        self.assertEquals("'type'", error_message.exception.key)

    # General Exception
    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_general_exception_without_name(self, text_method):
        field_data = {
            "type": "STRING",
            "css_selector": "#field",
            "input": "text"
        }
        text_method.side_effect = Exception("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertIn("Unhandled", error_message.exception.msg)

    @patch("the_ark.field_handlers.FieldHandler.handle_text")
    def test_dispatch_general_exception_with_name(self, text_method):
        field_data = {
            "type": "STRING",
            "css_selector": "#field",
            "input": "text",
            "name": "First Name"
        }
        text_method.side_effect = Exception("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.dispatch_field(field_data)
        self.assertIn(field_data["name"], error_message.exception.msg)

    # ===================================================================
    # --- Field Handler methods
    # ===================================================================
    # - Handle Text
    def test_handle_text_without_confirm(self):
        self.fh.handle_text("selector", "input text")
        self.sh.fill_an_element.assert_called_once_with(css_selector="selector", fill_text="input text")

    def test_handle_text_with_confirm(self):
        css_selector = "selector"
        input_text = "input text"
        confirm_css_selector = "confirm"
        self.fh.handle_text(css_selector, input_text, confirm_css_selector)
        self.sh.fill_an_element.assert_called_with(css_selector=confirm_css_selector, fill_text=input_text)

    def test_handle_text_selenium_exception(self):
        self.sh.fill_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                        "stacktrace",
                                                                                        "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_text("selector", "input text")

    def test_handle_text_general_exception(self):
        self.sh.fill_an_element.side_effect = Exception("Boo!")
        with self.assertRaises(FieldHandlerException):
            self.fh.handle_text("selector", "input text")

    # - Handle Check Box
    def test_handle_check_box(self):
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.2"}]
        self.fh.handle_check_box(enum, [0, 1])
        self.sh.click_an_element.assert_called_with(css_selector=enum[1]["css_selector"])

    def test_handle_check_box_key_error(self):
        enum = [{"bad_key": "selector.1"}, {"css_selector": "selector.2"}]
        with self.assertRaises(MissingKey):
            self.fh.handle_check_box(enum, [0, 1])

    def test_handle_check_box_selenium_exception(self):
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.2"}]
        self.sh.click_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                         "stacktrace",
                                                                                         "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_check_box(enum, [0, 1])

    def test_handle_check_box_general_exception(self):
        css_selector = "selenium"
        input_text = "input text"
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.handle_check_box(css_selector, input_text)
        self.assertIn("Unhandled", error_message.exception.msg)

    # - Handle Radio Button
    def test_handle_radio_button(self):
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.2"}]
        self.fh.handle_radio_button(enum, 1)
        self.sh.click_an_element.assert_called_with(css_selector=enum[1]["css_selector"])

    def test_handle_radio_button_key_error(self):
        enum = [{"bad_key": "selector.1"}, {"css_selector": "selector.1"}]
        with self.assertRaises(MissingKey):
            self.fh.handle_radio_button(enum, 0)

    def test_handle_radio_button_selenium_exception(self):
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.1"}]
        self.sh.click_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                         "stacktrace",
                                                                                         "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_radio_button(enum, 1)

    def test_handle_radio_button_general_exception(self):
        css_selector = "select.1"
        input_text = "input text"
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.handle_radio_button(css_selector, input_text)
        self.assertIn("Unhandled", error_message.exception.msg)

    # - Handle  Select
    def test_handle_select_with_first_invalid(self):
        selector = "select.1"
        self.fh.handle_select(selector, 1)
        self.sh.click_an_element.assert_called_once_with(css_selector="{0} option:nth-child({1})".format(selector, 3))

    def test_handle_select_with_first_valid(self):
        selector = "select.1"
        self.fh.handle_select(selector, 1, True)
        self.sh.click_an_element.assert_called_once_with(css_selector="{0} option:nth-child({1})".format(selector, 2))

    def test_handle_select_selenium_exception(self):
        self.sh.click_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                         "stacktrace",
                                                                                         "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_select("select.1", 1)

    def test_handle_select_general_exception(self):
        self.sh.click_an_element.side_effect = Exception("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.handle_select("select.1", 1)
        self.assertIn("Unhandled", error_message.exception.msg)

    # - Handle Drop Down
    def test_handle_drop_down(self):
        css_selector = "selector.1"
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.2"}]
        self.fh.handle_drop_down(css_selector, enum, 1)
        self.sh.click_an_element.assert_called_with(css_selector=enum[1]["css_selector"])

    def test_handle_drop_down_key_error(self):
        css_selector = "selector.1"
        enum = [{"bad_key": "selector.1"}, {"css_selector": "selector.1"}]
        with self.assertRaises(MissingKey):
            self.fh.handle_drop_down(css_selector, enum, 0)

    def test_handle_drop_down_selenium_exception(self):
        css_selector = "selector.1"
        enum = [{"css_selector": "selector.1"}, {"css_selector": "selector.1"}]
        self.sh.click_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                         "stacktrace",
                                                                                         "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_drop_down(css_selector, enum, 1)

    def test_handle_drop_down_general_exception(self):
        css_selector = "select.1"
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.handle_drop_down(css_selector, "break!", "break!")
        self.assertIn("Unhandled", error_message.exception.msg)

    # - Handle Button
    def test_handle_button(self):
        css_selector = "selector.1"
        self.fh.handle_button(css_selector)
        self.sh.click_an_element.assert_called_with(css_selector=css_selector)

    def test_handle_button_selenium_exception(self):
        css_selector = "selector.1"
        self.sh.click_an_element.side_effect = selenium_helpers.SeleniumHelperExceptions("message text",
                                                                                         "stacktrace",
                                                                                         "www.google.com")
        with self.assertRaises(SeleniumError):
            self.fh.handle_button(css_selector)

    def test_handle_button_general_exception(self):
        css_selector = "select.1"
        self.sh.click_an_element.side_effect = Exception("Boo!")
        with self.assertRaises(FieldHandlerException) as error_message:
            self.fh.handle_button(css_selector)
        self.assertIn("Unhandled", error_message.exception.msg)

    # ===================================================================
    # --- Field Handler Exception
    # ===================================================================
    def test_field_handler_exception_to_string_without_details(self):
        field_handler = FieldHandlerException("Message text")
        error_string = field_handler.__str__()
        self.assertNotIn("stacktrace", error_string)

    def test_field_handler_exception_to_string_with_details(self):
        field_handler = FieldHandlerException("message",
                                              "stacktrace:\nLine 1\nLine 2",
                                              {"css_selector": "selector.1"})
        error_string = field_handler.__str__()
        self.assertIn("css_selector", error_string)
        self.assertIn("stacktrace", error_string)

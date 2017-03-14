import unittest
from datetime import datetime, timedelta
from the_ark.field_handlers import CHECK_BOX_FIELD, SELECT_FIELD, STRING_FIELD, PHONE_FIELD, ZIP_CODE_FIELD, \
    DATE_FIELD, INTEGER_FIELD, EMAIL_FIELD, PASSWORD_FIELD
from the_ark import input_generator as ig
from the_ark.input_generator import InputGeneratorException
from mock import patch


class InputGeneratorTestCase(unittest.TestCase):
    @patch("random.random")
    def test_set_leave_blank(self, random_value):
        # - Tests without field data
        fake_blank = ig.set_leave_blank(1, True)
        self.assertEqual(fake_blank, False)

        # - Tests with field data
        # Not Required
        # - Blank
        random_value.return_value = 0.20
        fake_blank = ig.set_leave_blank(5, False)
        self.assertEqual(fake_blank, True)
        # - Not Blank
        random_value.return_value = 0.20
        fake_blank = ig.set_leave_blank(1, False)
        self.assertEqual(fake_blank, False)
        # -- Required
        fake_blank = ig.set_leave_blank(5, True)
        self.assertEqual(fake_blank, False)

    def test_check_min_vs_max(self):
        # - Test without a field
        with self.assertRaises(ig.InputGeneratorException):
            ig.check_min_vs_max(13, 12)

    # ===================================================================
    # --- dispatch_field() Tests
    # ===================================================================
    # - 'required' variable Test
    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_string_field_required(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "min": 10,
                      "max": 15,
                      "required": True}
        string_method.return_value = "return_value"
        ig.dispatch_field(field_data, 1)
        string_method.assert_called_once_with(field_data["min"], field_data["max"], 1, True)

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_string_field(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "min": 10,
                      "max": 15}
        string_method.return_value = "return_value"
        ig.dispatch_field(field_data, 1)
        string_method.assert_called_once_with(field_data["min"], field_data["max"], 1, False)

    # - Dispatch Integer
    @patch("the_ark.input_generator.generate_integer")
    def test_dispatch_integer_field_without_padding(self, integer_method):
        field_data = {"type": INTEGER_FIELD,
                      "min": 10,
                      "max": 15}

        integer_method.return_value = 3
        ig.dispatch_field(field_data, 1)
        integer_method.assert_called_once_with(field_data["min"], field_data["max"], 1, 1, False)

    @patch("the_ark.input_generator.generate_integer")
    def test_dispatch_integer_field_with_padding(self, integer_method):
        field_data = {"type": INTEGER_FIELD,
                      "min": 10,
                      "max": 15,
                      "padding": 10}

        integer_method.return_value = 3
        ig.dispatch_field(field_data, 1)
        integer_method.assert_called_once_with(field_data["min"], field_data["max"], 10, 1, False)

    # - Dispatch E-mail
    @patch("the_ark.input_generator.generate_email")
    def test_dispatch_email_field_without_domain(self, email_method):
        field_data = {"type": EMAIL_FIELD}
        email_method.return_value = "test@{0}".format(ig.DEFAULT_DOMAIN)
        ig.dispatch_field(field_data, 1)
        email_method.assert_called_once_with(ig.DEFAULT_DOMAIN, 1, False)

    @patch("the_ark.input_generator.generate_email")
    def test_dispatch_email_field_with_custom_domain(self, email_method):
        field_data = {"type": EMAIL_FIELD,
                      "domain": "gmail.com"}
        email_method.return_value = "test@gmail.com"
        ig.dispatch_field(field_data, 1)
        email_method.assert_called_once_with(field_data["domain"], 1, False)

    # - Dispatch Password
    def test_dispatch_password_generator_length(self):
        field_data = {"type": PASSWORD_FIELD}
        returned_password = ig.dispatch_field(field_data)
        self.assertTrue(len(returned_password) >= 6)

    def test_dispatch_password_generator_special_character(self):
        field_data = {"type": PASSWORD_FIELD}
        returned_password = ig.dispatch_field(field_data)
        self.assertTrue(any(character in returned_password for character in ig.SPECIAL_CHARACTER_LIST))

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_password_generator_error(self, string_method):
        string_method.side_effect = Exception('Boom!')
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_password()

    # - Dispatch Phone Number
    @patch("the_ark.input_generator.generate_phone")
    def test_dispatch_phone_field_defaults(self, phone_method):
        field_data = {"type": PHONE_FIELD}
        phone_method.return_value = "9878767654"
        ig.dispatch_field(field_data, 1)
        phone_method.assert_called_once_with(False, False, False, False, 1, False)

    @patch("the_ark.input_generator.generate_phone")
    def test_dispatch_phone_field_override_variables(self, phone_method):
        # - Using int values here instead of bools to verify determine the right params are changed
        field_data = {"type": PHONE_FIELD,
                      "decimal": 1,
                      "parenthesis": 2,
                      "dash": 3,
                      "space": 4}
        phone_method.return_value = "9878767654"
        ig.dispatch_field(field_data, 1)
        phone_method.assert_called_once_with(field_data["decimal"],
                                             field_data["parenthesis"],
                                             field_data["dash"],
                                             field_data["space"], 1, False)

    # - Dispatch ZIP Code
    @patch("the_ark.input_generator.generate_zip_code")
    def test_dispatch_zip_code_field_defaults(self, zip_method):
        field_data = {"type": ZIP_CODE_FIELD}
        zip_method.return_value = "99999"
        ig.dispatch_field(field_data, 1)
        zip_method.assert_called_once_with(1, False)

    # - Dispatch Index Field
    @patch("the_ark.input_generator.generate_index")
    def test_dispatch_index_field_without_random(self, index_method):
        field_data = {"type": SELECT_FIELD,
                      "enum": ["selector1", "selector2"]}
        index_method.return_value = 1
        ig.dispatch_field(field_data, 20)
        index_method.assert_called_once_with(len(field_data["enum"]), 20, False, False)

    @patch("the_ark.input_generator.generate_index")
    def test_dispatch_index_field_with_random(self, index_method):
        field_data = {"type": SELECT_FIELD,
                      "enum": ["selector1", "selector2"],
                      "random": True}
        index_method.return_value = 1
        ig.dispatch_field(field_data, 20)
        index_method.assert_called_once_with(len(field_data["enum"]), 20, False, True)

    # - Dispatch Check Box
    @patch("the_ark.input_generator.generate_check_box")
    def test_dispatch_check_box_field(self, check_box_method):
        field_data = {"type": CHECK_BOX_FIELD,
                      "enum": [{"selector1": "Selector 1"},
                               {"selector2": "Selector 2"}]}
        check_box_method.return_value = 1
        ig.dispatch_field(field_data, 150)
        check_box_method.assert_called_once_with(len(field_data["enum"]), 150, False)

    # - Dispatch Date
    @patch("the_ark.input_generator.generate_date")
    def test_dispatch_date_field_defaults(self, date_method):
        field_data = {"type": DATE_FIELD}
        date_method.return_value = "11/19/1911"
        ig.dispatch_field(field_data, 1)
        date_method.assert_called_once_with(ig.DEFAULT_START_DATE,
                                            ig.DEFAULT_END_DATE,
                                            ig.DEFAULT_DATE_FORMAT, 1, False)

    @patch("the_ark.input_generator.generate_date")
    def test_dispatch_date_field_override_variables(self, date_method):
        # - Using int values here instead of bools to verify determine the right params are changed
        field_data = {"type": DATE_FIELD,
                      "start_date": 1,
                      "end_date": 2,
                      "date_format": 3}
        date_method.return_value = "11/19/1911"
        ig.dispatch_field(field_data, 1)
        date_method.assert_called_once_with(field_data["start_date"],
                                            field_data["end_date"],
                                            field_data["date_format"], 1, False)

    # - Exceptions
    def test_dispatch_invalid_type(self):
        field_data = {"type": "pickles"}
        with self.assertRaises(ig.UnknownFieldType):
            ig.dispatch_field(field_data)

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_field_handler_exception_without_name(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "min": 10,
                      "max": 12}
        string_method.side_effect = ig.MissingKey("Hello", "key")
        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_field_handler_exception_with_name(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "name": "First Name",
                      "min": 10,
                      "max": 12}
        string_method.side_effect = ig.MissingKey("Hello", "key")
        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    def test_dispatch_key_error_without_name(self):
        field_data = {"type": STRING_FIELD,
                      "max": 12}

        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    def test_dispatch_key_error_with_name(self):
        field_data = {"type": STRING_FIELD,
                      "name": "First Name",
                      "max": 12}

        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_general_exception_without_name(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "min": 10,
                      "max": 12}

        string_method.side_effect = Exception("Boo!")
        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    @patch("the_ark.input_generator.generate_string")
    def test_dispatch_general_exception_exception_with_name(self, string_method):
        field_data = {"type": STRING_FIELD,
                      "name": "First Name",
                      "min": 10,
                      "max": 12}

        string_method.side_effect = Exception("Boo!")
        with self.assertRaises(ig.InputGeneratorException):
            ig.dispatch_field(field_data)

    # ===================================================================
    # --- Generate Input Tests
    # ===================================================================
    # - Generate String
    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_string_default_values(self, leave_blank):
        leave_blank.return_value = False
        returned_string = ig.generate_string()
        if not ig.DEFAULT_STRING_MIN <= len(returned_string) <= ig.DEFAULT_STRING_MAX:
            self.fail("The string length returned using the method defaults was incorrect. "
                      "It should be between {0} and {1} but was {2}".format(ig.DEFAULT_STRING_MIN,
                                                                            ig.DEFAULT_STRING_MAX,
                                                                            len(returned_string)))

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_string_blank_return(self, leave_blank):
        leave_blank.return_value = True
        self.assertEqual("", ig.generate_string())

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_string_specific_length(self, leave_blank):
        leave_blank.return_value = False
        # - Test string length ranges
        returned_string = ig.generate_string(15, 15)
        self.assertEqual(len(returned_string), 15)

    @patch("the_ark.input_generator.check_min_vs_max")
    def test_generate_string_general_exception(self, min_max):
        min_max.side_effect = Exception("Boo!")
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_string()

    # -- Generate Integer
    def test_generate_integer(self):
        # - Test default values
        returned_integer = ig.generate_integer()
        if not ig.DEFAULT_INTEGER_MIN <= len(returned_integer) <= ig.DEFAULT_INTEGER_MAX:
            self.fail("The integer length returned using the method defaults was incorrect. "
                      "It should be between {0} and {1} but was {2}".format(ig.DEFAULT_INTEGER_MIN,
                                                                            ig.DEFAULT_INTEGER_MAX,
                                                                            len(returned_integer)))

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_integer_blank_return(self, leave_blank):
        leave_blank.return_value = True
        self.assertEqual("", ig.generate_integer())

    def test_generate_integer_specific_range(self):
        returned_integer = ig.generate_integer(15, 15)
        self.assertEqual(returned_integer, "15")

    def test_generate_integer_with_padding(self):
        padding = 4
        returned_integer = ig.generate_integer(3, 8, padding)
        self.assertEqual(len(returned_integer), padding)

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_integer_exception(self, leave_blank):
        leave_blank.side_effect = Exception("Boo!")
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_integer("apples", "oranges")

    # - Generate Email
    def test_generate_email_default_values(self):
        returned_email = ig.generate_email()
        if ig.DEFAULT_DOMAIN not in returned_email:
            self.assertIn(ig.DEFAULT_DOMAIN, returned_email,
                          "The generated email did not include the default domain when the default parameters were "
                          "used. It should contain '{0}' but the returned email was: '{1}'".format(ig.DEFAULT_DOMAIN,
                                                                                                   returned_email))

    def test_generate_email_custom_domain(self):
        test_domain = "vincentrocks.com"
        returned_email = ig.generate_email(test_domain)
        if ig.DEFAULT_DOMAIN not in returned_email:
            self.assertIn(test_domain, returned_email,
                          "The generated email did not include the custom domain when a domain was passed in."
                          "It should contain '{0}' but the returned email was: '{1}'".format(test_domain,
                                                                                             returned_email))

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_email_blank_return(self, leave_blank):
        leave_blank.return_value = True
        returned_email = ig.generate_email()
        self.assertEqual("", returned_email)

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_email_exception(self, leave_blank):
        leave_blank.side_effect = Exception('Boom!')
        self.assertRaises(ig.InputGeneratorException, ig.generate_email)

    # -- Generate Phone
    def test_generate_phone_default_values(self):
        # Test default values ##########
        returned_phone = ig.generate_phone()
        self.assertRegexpMatches(returned_phone, "^\d{10}")

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_phone_blank_return(self, leave_blank):
        leave_blank.return_value = True
        returned_phone = ig.generate_phone()
        self.assertEqual(returned_phone, "")

    def test_generate_phone_all_dashed(self):
        # Check for ### -### -####
        returned_phone = ig.generate_phone(dash=True)
        self.assertRegexpMatches(returned_phone, "^[2-9]\d{2}-\d{3}-\d{4}")

    def test_generate_phone_all_spaces(self):
        # Check for ### ### ####
        returned_phone = ig.generate_phone(space=True)
        self.assertRegexpMatches(returned_phone, "^[2-9]\d{2}\s\d{3}\s\d{4}")

    def test_generate_phone_parenthesis_and_dash(self):
        # Check for (###)### -####
        returned_phone = ig.generate_phone(parenthesis=True, dash=True)
        self.assertRegexpMatches(returned_phone, "^\(\d{3}\)\d{3}-\d{4}")

    def test_generate_phone_just_parenthesis(self):
        # Check for (###)#######
        returned_phone = ig.generate_phone(parenthesis=True)
        self.assertRegexpMatches(returned_phone, "^\(\d{3}\)\d{7}")

    def test_generate_phone_parenthesis_dash_space(self):
        # Check for (###) ### -####
        returned_phone = ig.generate_phone(parenthesis=True, dash=True, space=True)
        self.assertRegexpMatches(returned_phone, "\(\d{3}\)\s\d{3}-\d{4}")

    def test_generate_phone_all_decimals(self):
        # Check for ###.###.####
        returned_phone = ig.generate_phone(decimals=True)
        self.assertRegexpMatches(returned_phone, "^[2-9]\d{2}\.\d{3}\.\d{4}")

    def test_generate_phone_decimal_override(self):
        # Decimals override everything
        returned_phone = ig.generate_phone(decimals=True, parenthesis=True, dash=True, space=True)
        self.assertRegexpMatches(returned_phone, "^[2-9]\d{2}\.\d{3}\.\d{4}")

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_phone_exception(self, leave_blank):
        leave_blank.side_effect = Exception('Boom!')
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_phone(1)

    # - Generate ZIP Code
    def test_generate_zip_default_values(self):
        returned_zip = ig.generate_zip_code()
        self.assertEqual(len(returned_zip), 5)

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_zip_blank_return(self, leave_blank):
        leave_blank.return_value = True
        returned_zip = ig.generate_zip_code()
        self.assertEqual("", returned_zip)

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_zip_exception(self, leave_blank):
        # Test the General Exception catch
        leave_blank.side_effect = Exception('Boom!')
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_zip_code()

    # - Generate Index
    def test_generate_index_default_values(self):
        returned_index = ig.generate_index()
        if returned_index not in range(0, 2):
            self.fail("The index generated using the method defaults was incorrect. "
                      "It should be between 0 and {0} but was {1}".format(ig.DEFAULT_INDEX_OPTIONS, returned_index))

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_index_blank_return(self, leave_blank):
        leave_blank.return_value = True
        self.assertEqual("", ig.generate_index())

    def test_generate_index_last_option(self):
        index = 5
        self.assertEqual(ig.generate_index(index, 5), index - 1)

    def test_generate_index_always_random(self):
        generated_indexes = []
        for i in range(0, 10):
            generated_indexes.append(ig.generate_index(100, always_random=True))
        if all(x == generated_indexes[0] for x in generated_indexes):
            self.fail("The indexes generated in the Always Random check were not different!")

    def test_generate_index_all_options_used(self):
        generated_indexes = []
        for i in range(0, 10):
            generated_indexes.append(ig.generate_index(100, test_number=1000))
        if all(x == generated_indexes[0] for x in generated_indexes):
            self.fail("The indexes generated in the Always Random check were not different!")

    def test_generate_index_exception(self):
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_index(["apples", "pickles"], 500)

    # - Generate Check Box
    def test_generate_check_box_default_values(self):
        returned_index = ig.generate_check_box()
        if not isinstance(returned_index, list):
            self.fail("The index array generated by the default parameters was not... an array. "
                      "It should be a list, but this was returned: {0}".format(returned_index))

    @patch("random.random")
    def test_generate_check_box_not_required_blank(self, random_result):
        random_result.return_value = .20
        self.assertEqual([], ig.generate_check_box(2, 10, False))

    @patch("random.random")
    def test_generate_check_box_not_required_not_blank(self, random_result):
        random_result.return_value = .50
        self.assertIsInstance(ig.generate_check_box(2, 10, False), list)

    @patch("random.random")
    def test_generate_check_box_random_choice_select_each(self, random_result):
        random_result.return_value = .50
        generated_indexes = ig.generate_check_box(5, 10)
        self.assertEqual(len(generated_indexes), 5)

    @patch("random.random")
    def test_generate_check_box_random_choice_select_all(self, random_result):
        random_result.return_value = .50
        self.assertEqual([1], ig.generate_check_box(2, 2))

    def test_generate_check_box_exception(self):
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_check_box("apples")

    # - Generate Date
    def test_generate_date(self):
        returned_date = ig.generate_date()
        try:
            datetime.strptime(returned_date, ig.DEFAULT_DATE_FORMAT)
        except Exception as e:
            self.fail("The default settings for generate_date() did not return a date in the default format "
                      "of {0}. The date returned was '{1}': {2}".format(ig.DEFAULT_DATE_FORMAT, returned_date, e))

    @patch("the_ark.input_generator.set_leave_blank")
    def test_generate_date_blank_return(self, leave_blank):
        leave_blank.return_value = True
        returned_date = ig.generate_date()
        self.assertEqual("", returned_date, "The check for blank dates did not return a blank string")

    def test_generate_date_range_past_int(self):
        start_date = 4
        end_date = 2
        expected_date_format = ig.DEFAULT_DATE_FORMAT
        returned_date = ig.generate_date(start_date, end_date)
        try:
            formatted_date = datetime.strptime(returned_date, ig.DEFAULT_DATE_FORMAT).date()
        except Exception as e:
            self.fail("When checking the date range, could not convert the returned date into '{0}' format in "
                      "order to compare the dates. The returned date was {1}: {2}".format(expected_date_format,
                                                                                          returned_date, e))
        # Returned Date older than current date
        self.assertGreater(datetime.now().date(), formatted_date,
                           "When using days, in the past, the returned date was not older than the current date")
        # Returned Date older than end date
        self.assertGreater((datetime.now() - timedelta(days=end_date)).date(),
                           formatted_date,
                           "When using days, in the past, the returned date was not older than the end date")

    def test_generate_date_range_past_date(self):
        # - Past in dates (%Y-%m-%d) with "%Y/%d/%m" format
        expected_format = "%Y/%d/%m"
        start_date = datetime.strptime("19800404", "%Y%m%d").date()
        end_date = datetime.strptime("20150325", "%Y%m%d").date()
        returned_date = ig.generate_date(str(start_date), str(end_date), expected_format)
        # - Check returned date format
        try:
            formatted_date = datetime.strptime(returned_date, expected_format).date()
        except Exception as e:
            self.fail("When checking the date range with custom format, could not convert the returned date into '{0}'"
                      " format in order to compare the dates. The returned date was {1}: {2}"
                      .format(expected_format, returned_date, e))
        # Returned Date older than current date
        self.assertGreater(formatted_date, start_date,
                           "When using dates, in the past, the returned date was not older than the start date")
        # Returned Date older than end date
        self.assertGreater(end_date, formatted_date,
                           "When using dates, in the past, the returned date was not older than the end date")

    def test_generate_date_range_future_int(self):
        # - Date Range Checks (in the FUTURE!!! *cue sci-fi sound effects)
        start_date = -4
        end_date = -20
        expected_date_format = ig.DEFAULT_DATE_FORMAT
        returned_date = ig.generate_date(start_date, end_date)
        try:
            formatted_date = datetime.strptime(returned_date, ig.DEFAULT_DATE_FORMAT).date()
        except Exception as e:
            self.fail("When checking the date range in the future, could not convert the returned date into '{0}' "
                      "format in order to compare the dates. The returned date was {1}: {2}"
                      .format(expected_date_format, returned_date, e))
        # Returned Date later than current date
        self.assertGreater(formatted_date, datetime.now().date(),
                           "When using days, in the future, the returned date was not later than the current date")
        # Returned Date older than end date
        self.assertGreater((datetime.now() - timedelta(days=end_date)).date(), formatted_date,
                           "When using days, in the past, the returned date was not older than the end date")

    def test_generate_date_range_future_date(self):
        # Future in dates (%Y-%m-%d) with "%m-%d-%y" format
        expected_future_format = "%m-%d-%y"
        start_date = datetime.strptime("20250404", "%Y%m%d").date()
        end_date = datetime.strptime("20300325", "%Y%m%d").date()
        returned_date = ig.generate_date(str(start_date), str(end_date), expected_future_format)
        # - Check returned date format
        try:
            formatted_date = datetime.strptime(returned_date, expected_future_format).date()
        except Exception as e:
            self.fail("When checking the future date range with custom format, could not convert the returned date "
                      "into '{0}' format in order to compare the dates. The returned date was {1}: {2}"
                      .format(expected_future_format, returned_date, e))
        # Returned Date later than current date
        self.assertGreater(formatted_date, datetime.now().date(),
                           "When using dates, in the future, the returned date was not later than the start date")
        # Returned Date older than end date
        self.assertGreater(end_date, formatted_date,
                           "When using dates, in the future, the returned date was not older than the end date")

    def test_generate_date_date_exception(self):
        # - Without field
        with self.assertRaises(ig.InputGeneratorException):
            ig.generate_date("apples")

    # ===================================================================
    # --- Field Handler Exception
    # ===================================================================
    def test_input_generator_exception_to_string_without_details(self):
        input_exc = InputGeneratorException("Message text")
        error_string = input_exc.__str__()
        self.assertNotIn("stacktrace", error_string)

    def test_field_handler_exception_to_string_with_details(self):
        input_exc = InputGeneratorException("message",
                                            "stacktrace:\nLine 1\nLine 2",
                                            {"css_selector": "selector.1"})
        error_string = input_exc.__str__()
        self.assertIn("css_selector", error_string)
        self.assertIn("stacktrace", error_string)

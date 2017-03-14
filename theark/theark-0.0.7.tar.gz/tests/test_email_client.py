from the_ark.email_client import EmailClient, EmailClientException
import mandrill
from mock import patch
import unittest


class EmailClientTestCase(unittest.TestCase):
    @patch("mandrill.Messages.send")
    def test_successful_send(self, send):
        send.return_value = "Success!"
        ec = EmailClient("fake_key")
        ec.send_email("from.test@test.com", ["to.test@test.com"], "Message Text")
        send.assert_called_once_with(message={'from_email': 'from.test@test.com', 'from_name': 'The Ark',
                                              'html': 'Message Text', 'to': [{'email': 'to.test@test.com'}],
                                              'subject': 'A Message From The Ark'})

    @patch("mandrill.Messages.send")
    def test_unsuccessful_send(self, send):
        send.side_effect = mandrill.Error()
        ec = EmailClient("fake_key")
        with self.assertRaises(EmailClientException) as error_message:
            ec.send_email("from.test@test.com", ["to.test@test.com"], "Message Text")
        self.assertIn("Mandrill Error", str(error_message.exception.msg))

    @patch("mandrill.Messages.send")
    def test_invalid_from_email(self, send):
        send.side_effect = mandrill.Error()
        ec = EmailClient("fake_key")
        with self.assertRaises(EmailClientException) as error_message:
            ec.send_email("from.test@test", ["to.test@test.com"], "Message Text")
        self.assertIn("FROM", error_message.exception.msg)

    @patch("mandrill.Messages.send")
    def test_invalid_to_emails_object(self, send):
        send.side_effect = mandrill.Error()
        ec = EmailClient("fake_key")
        with self.assertRaises(EmailClientException) as error_message:
            ec.send_email("from.test@test.com", "to.test@test.com", "Message Text")
        self.assertIn("List", error_message.exception.msg)

    @patch("mandrill.Messages.send")
    def test_invalid_to_email(self, send):
        send.side_effect = mandrill.Error()
        ec = EmailClient("fake_key")
        bad_email = "bad.to.email@test"
        with self.assertRaises(EmailClientException) as error_message:
            ec.send_email("from.test@test.com", ["good.to.test@test.com", bad_email], "Message Text")
        self.assertIn("TO", error_message.exception.msg)
        self.assertIn(bad_email, error_message.exception.msg)

    # ===================================================================
    # --- Email Client Exceptions
    # ===================================================================
    def test_field_handler_exception_to_string_without_details(self):
        field_handler = EmailClientException("Message text")
        error_string = field_handler.__str__()
        self.assertNotIn("stacktrace", error_string)

    def test_field_handler_exception_to_string_with_details(self):
        error_exception = EmailClientException("message",
                                               "stackittytrace:\nLine 1\nLine 2",
                                               {"from_email": "test@test.com"})
        error_string = error_exception.__str__()
        self.assertIn("test@test.com", error_string)
        self.assertIn("stackittytrace", error_string)

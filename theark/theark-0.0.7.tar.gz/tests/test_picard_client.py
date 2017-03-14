import unittest
from mock import patch, Mock

from the_ark import picard_client

picard_client_obj = None


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.picard_client_obj = picard_client.PicardClient()

    @patch('requests.post')
    def test_send_to_picard(self, requests_post):
        r = Mock()
        r.status_code = 200
        r.text = '{"first_name": "bill"}'
        requests_post.return_value = r
        self.assertEqual(self.picard_client_obj.send_to_picard
                         ('url', 'data',
                          self.picard_client_obj.create_headers()),
                         {"first_name": "bill"})
        self.assertEqual(self.picard_client_obj.send_to_picard
                         ('url', 'data'),
                         {"first_name": "bill"})

    @patch('requests.post')
    def test_send_to_picard_400(self, requests_post):
        r = Mock()
        r.status_code = 400
        r.text = 'tish broke'
        requests_post.return_value = r

        self.assertRaises(picard_client.PicardClientException, self.picard_client_obj.send_to_picard, '', '', '')

        r.status_code = 303
        self.assertRaises(picard_client.PicardClientException, self.picard_client_obj.send_to_picard, '', '', '')

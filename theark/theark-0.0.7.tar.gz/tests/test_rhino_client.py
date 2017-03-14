import unittest

from mock import patch, Mock
from the_ark import rhino_client

__author__ = 'chaley'


rhino_client_ojb = None


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.rhino_client_obj = rhino_client.RhinoClient('test_name',
                                                         'url', 'brand',
                                                         'branch', 'build_id',
                                                         'user',
                                                         'rhino_client_url')

    def test_set_log(self):
        self.rhino_client_obj.set_log("file_path", "link_text")
        self.assertEqual('file_path',
                         self.rhino_client_obj.test_data['result_url'])
        self.assertEqual('link_text',
                         self.rhino_client_obj.test_data['result_text'])

    @patch('requests.get')
    def test_get(self, requests_get):
        r = Mock()
        r.json.return_value = {"stuff": "stuff"}
        requests_get.return_value = r
        response = self.rhino_client_obj.get('test_id')
        self.assertEqual({"stuff": "stuff"}, response)

    @patch('requests.post')
    def test_post(self, requests_post):
        request_json = Mock()
        request_json.status_code = 201
        requests_post.return_value = request_json
        self.rhino_client_obj.post()

        self.assertEqual(True, self.rhino_client_obj.posted)

    @patch('requests.post')
    def test_post_fail(self, requests_post):
        request_json = Mock()
        request_json.status_code = 400
        requests_post.return_value = request_json

        self.assertRaises(Exception, self.rhino_client_obj.post)

    @patch('requests.put')
    def test_put(self, requests_put):
        self.rhino_client_obj.test_data['test_id'] = 156465465
        self.rhino_client_obj.posted = True

        request_json = Mock()
        request_json.status_code = 201
        request_json.json.return_value = {"stuff": "stuff"}

        requests_put.return_value = request_json
        self.rhino_client_obj.put()

        self.assertEqual(True, self.rhino_client_obj.posted)

    def test_put_posted_false(self):

        self.assertRaises(Exception, self.rhino_client_obj.put)

    @patch('requests.put')
    def test_put_status_false(self, requests_put):
        self.rhino_client_obj.test_data['test_id'] = 156465465
        self.rhino_client_obj.posted = True

        request_json = Mock()
        request_json.status_code = 500
        requests_put.return_value = request_json
        self.assertRaises(rhino_client.RhinoClientException,
                          self.rhino_client_obj.put)

    @patch('requests.post')
    def test_send_test_post(self, requests_post):
        request_json = Mock()
        request_json.status_code = 201
        requests_post.return_value = request_json
        self.rhino_client_obj.send_test("status")

        self.assertEqual(True, self.rhino_client_obj.posted)

    @patch('requests.put')
    def test_send_test_put(self, requests_put):
        self.rhino_client_obj.test_data['test_id'] = 156465465
        self.rhino_client_obj.posted = True

        request_json = Mock()
        request_json.status_code = 201

        requests_put.return_value = request_json
        self.rhino_client_obj.send_test("status")

        self.assertEqual(True, self.rhino_client_obj.posted)

if __name__ == '__main__':
    unittest.main()

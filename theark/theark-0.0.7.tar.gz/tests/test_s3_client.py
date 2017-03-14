import unittest
import urlparse
from the_ark.s3_client import S3Client, S3ClientException
from mock import Mock, patch
from boto.s3.key import Key
from cStringIO import StringIO

__author__ = 'chaley'

bucket = "some bucket"
s3_link_url = "http://qa-projects.s3.amazonaws.com/hippo/screenshots/valcyte/test/0EEC852C64F4/screenshot_log.html"
url_parse_base = urlparse.urlparse(s3_link_url)
s3_security_link_url = "http://qa-projects.s3.amazonaws.com/hippo/screenshots/valcyte/test/0EEC852C64F4/screenshot_log.html?x-amz-security-token=FQoDYXdzEDYaDDFi4AMLv/N0suzGZSKcA/fEWU1skiy7HOgF/6m8hFwi5Zg5l5nx/Z8HVVtRLvP6c25Ut7QMCIiszRChoIMXfGXHs04aNYU8xvNKXlAxu9MwSqMK0SwDMB3vb4Hb3CIoLX1tDIT/xeBTEqELg/KZxEcOOnnRHBxlg7KajiyCmwpaoRJqkIpRvibrsWIiXrNsvc35zHOn6ZbQs8qFB9JwRTCpqxvtIcaaCPjXUA0K4gwqgwwTq5UC89awj7uijXN2LwmRUQgy6ZvcoNmoxHvMYuoNE%2B6f21WS07I%2BjJFir%2BWNVe3J8YxIXCqGtcmeFn%2BqAz68zTKJVQ2chKrnZf0VoQpUdekr2B6eQojWdoxpMRUNuTm1/5iO3t28w7Lwri900A6Zr9nMh7qqTkFyh5h9RSYv/jvQE0yPcaVwnGmNADfH28uj2j0ucN0sOAvZEdwDVvW8vh6q8ENc6Z/5yu4oOyjWG4rBhxE8ZniOKbMeOwNS3gWYIA1cxJJ8NVSsDP%2BfucOQH//YKC4jFYaGUF9lPmxMlP01c0OFw9n0Ozc6y/sfWfuSaJOj0J8pL20oj6yfwAU%3D"
url_parse_sec_token = urlparse.urlparse(s3_security_link_url)


class S3InitTestCase(unittest.TestCase):
    @patch('boto.s3.connection.S3Connection')
    def test_class_init(self, s3con):
        s3con.return_value = {}
        client = S3Client(bucket)
        self.assertIsNotNone(client)

    @patch('boto.s3.connection.S3Connection')
    def test_class_init_fail(self, s3con):
        s3con.side_effect = Exception('Boom')
        client = S3Client(bucket)
        self.assertIsNone(client.s3_connection)


class S3MethodTestCase(unittest.TestCase):
    def setUp(self):
        self.client = S3Client(bucket)
        self.client.s3_connection = Mock()
        self.client.bucket = Mock()

    @patch('boto.s3.connection.S3Connection')
    def test_connect(self, s3_cls):
        cls_inst = Mock()
        s3_cls.return_value = cls_inst

        # Set the client connection to None for testing connect
        self.client.s3_connection = None

        self.client.connect()

        s3_cls.assert_called_once_with(is_secure=False)
        cls_inst.get_bucket.assert_called_once_with('some bucket', validate=False)

        # make it go boom
        self.client.s3_connection = None
        s3_cls.side_effect = Exception('Boom!')

        self.assertRaises(Exception, self.client.connect)

    def test_generate_path(self):
        self.assertEqual('s3_path/file_to_store',
                         self.client._generate_file_path("/s3_path",
                                                         "file_to_store"))
        self.assertEqual('s3_path/file_to_store',
                         self.client._generate_file_path("s3_path/",
                                                         "file_to_store"))
        self.assertEqual('s3_path/file_to_store',
                         self.client._generate_file_path("s3_path",
                                                         "file_to_store/"))
        self.assertEqual('s3_path/file_to_store',
                         self.client._generate_file_path(
                             "/s3_path/", "///////file_to_store/"))
        self.assertEqual('qa/tools/marketing/file_to_store',
                         self.client._generate_file_path(
                             "/qa/tools/marketing", "file_to_store/"))

    def test_verify_file(self):
        self.client.bucket.get_key.return_value = None
        self.assertFalse(self.client.verify_file("s3_path", "file_to_store"))

        self.client.bucket.get_key.return_value = "testing"
        self.assertTrue(self.client.verify_file("s3_path", "file_to_store"))

    def test_verify_file_boom(self):
        self.client.bucket.get_key.side_effect = Exception(
            'Here Comes the Boom!')
        with self.assertRaises(S3ClientException):
            self.client.verify_file('stuff', 'more stuff')

    @patch('the_ark.s3_client.S3Client.verify_file')
    def test_get_file(self, verify):
        mock_file = Mock()
        verify.return_value = True
        self.client.bucket.get_key.return_value = mock_file
        self.client.get_file('stuff', 'more stuff')

        self.client.bucket.get_key.assert_called_once_with(
            'stuff/more stuff')

    @patch('the_ark.s3_client.S3Client.verify_file')
    def test_get_file_with_no_file(self, verify):
        mock_file = Mock()
        verify.return_value = False
        self.client.bucket.get_key.return_value = mock_file
        with self.assertRaises(S3ClientException):
            self.client.get_file('stuff', 'more stuff')

    def test_get_file_boom(self):
        self.client.bucket.get_key.side_effect = Exception(
            'Here Comes the Boom!')
        with self.assertRaises(S3ClientException):
            self.client.get_file('stuff', 'more stuff')

    def test_store_file_boom(self):
        with self.assertRaises(S3ClientException):
            self.client.store_file('stuff', 'more stuff', 'file_name')

        with self.assertRaises(S3ClientException):
            self.client.store_file('stuff', 'more stuff', filename="bob's file")

    @patch('urlparse.urlparse')
    @patch('mimetypes.guess_type')
    @patch('boto.s3.key.Key.set_contents_from_file')
    def test_store_file(self, set_contents, guess_type, url_parse):
        url_parse.return_value = url_parse_base.scheme, url_parse_base.netloc, url_parse_base.path, \
                                 url_parse_base.params, url_parse_base.query, url_parse_base.fragment
        guess_type.return_value("image/png")
        set_contents.return_value(True)
        self.client.store_file(
            'stuff', "./tests/etc/all_black.png", return_url=True, filename="this file")

        self.client.store_file(
            'stuff', "./tests/etc/all_black.png", return_url=False, filename="this file")

    @patch('urlparse.urlparse')
    @patch('mimetypes.guess_type')
    @patch('boto.s3.key.Key.set_contents_from_file')
    def test_store_file_with_security_token(self, set_contents, guess_type, url_parse):
        url_parse.return_value = url_parse_sec_token.scheme, url_parse_sec_token.netloc, url_parse_sec_token.path, \
                                 url_parse_sec_token.params, url_parse_sec_token.query, url_parse_sec_token.fragment
        guess_type.return_value("image/png")
        set_contents.return_value(True)
        returned_url = self.client.store_file('stuff', 1, return_url=True, filename="this file")
        self.assertEqual(returned_url, s3_link_url)

    @patch('boto.s3.bucket.Bucket.list')
    def test_get_all_filenames_in_folder(self, mock_list):
        mock_list.return_value = []
        self.client.get_all_filenames_in_folder('path')

    def test_get_most_recent_file_from_s3_key_list(self):
        first = Key()
        second = Key()
        third = Key()
        first.last_modified = 3
        second.last_modified = 4
        third.last_modified = 1
        key_list = [first, second, third]

        most_recent_key = self.client. \
            get_most_recent_file_from_s3_key_list(key_list)
        self.assertEqual(
            most_recent_key.last_modified, key_list[1].last_modified)

    @patch('tempfile.mkdtemp')
    @patch('os.path.getsize')
    def test_split_file_boom(self, get_size, make_dir):
        make_dir.side_effect = Exception('Here Comes the Boom?')
        get_size.return_value = 9999999999999
        with self.assertRaises(S3ClientException):
            self.client.store_file(
                'stuff', "./tests/etc/test.png", return_url=False, filename="this file")

    @patch('urlparse.urlparse')
    @patch('mimetypes.guess_type')
    @patch('boto.s3.key.Key.set_contents_from_file')
    @patch('os.path.getsize')
    def test_store_file_with_split(self, get_size, set_contents, guess_type, url_parse):
        url_parse.return_value = url_parse_sec_token.scheme, url_parse_sec_token.netloc, url_parse_sec_token.path, \
                                 url_parse_sec_token.params, url_parse_sec_token.query, url_parse_sec_token.fragment
        guess_type.return_value("image/png")
        set_contents.return_value(True)
        get_size.return_value = 9999999999999
        self.client.store_file(
            'stuff', "./tests/etc/test.png", return_url=True, filename="this file")

        self.client.store_file(
            'stuff', "./tests/etc/test.png", return_url=False, filename="this file")

    @patch('urlparse.urlparse')
    @patch('mimetypes.guess_type')
    @patch('boto.s3.key.Key.set_contents_from_file')
    def test_store_file_with_stringIO(self, set_contents, guess_type, url_parse):
        url_parse.return_value = url_parse_sec_token.scheme, url_parse_sec_token.netloc, url_parse_sec_token.path, \
                                 url_parse_sec_token.params, url_parse_sec_token.query, url_parse_sec_token.fragment
        guess_type.return_value("image/png")
        set_contents.return_value(True)
        image_file = StringIO()
        with open("./tests/etc/test.png") as f:
            image_file.write(f.read())
        image_file.seek(0)
        self.client.store_file(
            'stuff', image_file, return_url=True, filename="this file")

        self.client.store_file(
            'stuff', image_file, return_url=False, filename="this file")


if __name__ == '__main__':
    unittest.main()

from dial import Dialer
from nose.tools import assert_equal
from nose.tools import assert_not_equal


# Using http://jsonplaceholder.typicode.com/posts/1 for sample API
class TestDialer():

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    def test_init(self):
        # Test with all properties
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request = {'header': {'Content-Type': 'application/json'},
                   'cookie': {'test-cookie': '1'}}
        request_str = {'header': 'Content-Type:application/json',
                       'cookie': 'test-cookie:1'}
        string = url + " " + method + " " + str(request['header']) \
            + " " + str(request['cookie'])
        d = Dialer(url, method, request_str)

        assert_equal(d.to_string(), string)

    def test_init_without_header(self):
        # Test init without header
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request = {'header': {}, 'cookie': {'test-cookie': '1'}}
        request_str = {'cookie': 'test-cookie:1'}
        string = url + " " + method + " " + str(request['header']) \
            + " " + str(request['cookie'])
        d = Dialer(url, method, request_str)
        assert_equal(d.to_string(), string)

    def test_init_without_header_cookie(self):
        # Test init without cookie or header
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request = {'header': {}, 'cookie': {}}
        request_str = {}
        string = url + " " + method + " " + str(request['header']) \
            + " " + str(request['cookie'])
        d = Dialer(url, method, request_str)
        assert_equal(d.to_string(), string)

    def test_init_without_cookie(self):
        # Test init without cookie or header
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request = {'header': {'Content-Type': 'application/json'},
                   'cookie': {}}
        request_str = {'header': 'Content-Type:application/json'}
        string = url + " " + method + " " + str(request['header']) \
            + " " + str(request['cookie'])
        d = Dialer(url, method, request_str)
        assert_equal(d.to_string(), string)

    # test with a simple success API
    def test_dial_without_exception(self):
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request_str = {}
        d = Dialer(url, method, request_str)
        assert_equal(d.dial_without_exception(), True)
        assert_not_equal(d.dial_without_exception(), False)

    # dial and check json
    def test_dial_and_parse_json(self):
        url = "http://jsonplaceholder.typicode.com/posts/1"
        method = "GET"
        request_str = {}
        d = Dialer(url, method, request_str)
        # Check JSON Value
        js = d.dial_and_parse_json()
        assert_equal(js['userId'], 1)
        assert_equal(js['id'], 1)

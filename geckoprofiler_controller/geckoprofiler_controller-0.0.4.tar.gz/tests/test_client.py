import unittest

from tests.mock_addon import MockAddon
from geckoprofiler_controller.control_client import *
from geckoprofiler_controller.control_server import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

        # create Mock Add-on
        self.mockaddon = MockAddon()

        # Starting server ...
        self.my_server = ServerController()
        self.my_server.start_server()
        time.sleep(5)

        # start Mock Add-on
        self.mockaddon.start_addon()

        # create Python client
        self.my_client = ControllerClient(control_server=self.my_server, save_path=self.CURRENT_PATH)
        # Python client connect to server
        self.my_client.connect()

    def test_client_file(self):
        # Opening profiling page ...
        self.my_client.open_profiling_page()
        # Getting profiling file ...
        filepath = self.my_client.get_profiling_file()
        self.assertEqual(filepath, os.path.join(self.CURRENT_PATH, 'FirefoxProfile.json.gz'))
        self.mockaddon.reset_addon()

    def test_client_link(self):
        # Opening profiling page ...
        self.my_client.open_profiling_page()
        # Getting profiling link ...
        link = self.my_client.get_profiling_link()
        self.assertEqual(link, 'https://perfht.ml/2lQhjU8')
        self.mockaddon.reset_addon()

    def test_client_wait_share(self):
        # Opening profiling page ...
        self.my_client.open_profiling_page()
        # Waiting sharing finish ...
        ret = self.my_client.wait_profiling_link_sharing_finish()
        self.assertEqual(ret, True)
        self.mockaddon.reset_addon()

    def test_client_wait_share_faile(self):
        # Do not open profiling page ...
        # Waiting sharing finish ...
        ret = self.my_client.wait_profiling_link_sharing_finish()
        self.assertEqual(ret, False)
        self.mockaddon.reset_addon()

    def tearDown(self):
        # stop Mock Add-on
        self.mockaddon.stop_addon()

        # Close server and disconnect
        self.my_client.send_stop_server_command()
        self.my_client.disconnect()
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()

from geckoprofiler_controller.control_client import *
from geckoprofiler_controller.control_server import *

from tests.mock_addon import MockAddon

logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    # mockaddon = MockAddon()
    my_client = None

    try:
        CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

        # Starting server ...
        print('Starting Web Socket server ...')
        my_server = ServerController()
        my_server.start_server()
        time.sleep(5)
        print('Web Socket server started.')

        # wait for user actions on Firefox
        print('\n\n'
              '############################################################\n'
              '# Now you can launch Firefox with Gecko-Profiler (Hasal),  #\n'
              '# and then access web sites.                               #\n'
              '############################################################')
        raw_input('>> Press Enter will start profiling ... <<\n\n')

        # starting mock Add-on
        # mockaddon.start_addon()

        # Starting client ...
        my_client = ControllerClient(control_server=my_server, save_path=CURRENT_PATH)
        my_client.connect()

        # Opening profiling page ...
        my_client.open_profiling_page()

        # Getting profiling file ...
        filepath = my_client.get_profiling_file()

        # Getting profiling link ...
        link = my_client.get_profiling_link()

        # wait for sharing finish
        print('Wait for sharing finish ...')
        if my_client.wait_profiling_link_sharing_finish():
            print('Sharing finished.')
        else:
            print('Sharing timeout.')

        print('>> Profiling File: {}'.format(filepath))
        print('>> Profiling Link: {}'.format(link))
    finally:
        # mockaddon.stop_addon()

        # Close server and disconnect
        my_client.send_stop_server_command()
        my_client.disconnect()
        print('stop server.')

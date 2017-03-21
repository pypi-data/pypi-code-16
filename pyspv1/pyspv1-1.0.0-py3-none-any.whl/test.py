from spv1dll import Spv1Dll
from spv1 import STRUCT_SPV1FRAME
from serialcommspv1 import SerialCommSpv1
from spsc import EnumLogFilter

#print (__name__)
if __name__ == "__main__":
    # only works if test is running from source - not from package
    print("pyspv1 test.py is running")
    class AsyncHandler():
        def dll_callback_async_rx_protocol(self, rx_spv1_frame: STRUCT_SPV1FRAME):
            print("Async Command/Response received:", hex(rx_spv1_frame.command))


    spv1dll = Spv1Dll()
    spv1dll.initialize(path="testspv1mifare.dll",vertical_log=True,log_filter=EnumLogFilter.ALL)
    async_handler_test = AsyncHandler()  # async_card_read_callback=card_read_callback)
    mifare_serial_comm = SerialCommSpv1(spv1dll, async_handler_test,AsyncReceive=False)
    if mifare_serial_comm.open_port('COM17', 19200) != True:
        print("Failed to opening com port")
        quit()
    #mifare_serial_comm.close_port()
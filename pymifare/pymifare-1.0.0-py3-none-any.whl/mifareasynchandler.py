from pyspv1.spv1 import STRUCT_SPV1FRAME
from mifaredef import Def_MIFARE_COMMANDS
from cmdchangebaudrate import CmdChangeBaudrate
from cmdactivateall import CmdActivateAll
from cmdfirmware import CmdFirmware


class MifareAsyncHandler():
    def __init__(self,spv1handler,async_card_read_callback=None):
        self.async_card_read_callback = async_card_read_callback
        self.spv1handler = spv1handler

    def register_async_card_read_callback(self,callback):
        self.async_card_read_callback = callback


    def dll_callback_async_rx_protocol(self, rx_spv1_frame: STRUCT_SPV1FRAME):
        if (rx_spv1_frame.command == Def_MIFARE_COMMANDS.ACTIVATE_ALL) or \
                (rx_spv1_frame.command == Def_MIFARE_COMMANDS.SEEK_FOR_TAG):

            cmd_activate_all = CmdActivateAll()
            self.spv1handler.response_builder_helper(cmd_activate_all,rx_spv1_frame)

            if self.async_card_read_callback!=None:
                self.async_card_read_callback(cmd_activate_all)

        elif rx_spv1_frame.command == Def_MIFARE_COMMANDS.FIRMWARE:

            cmd_firmware = CmdFirmware()
            self.spv1handler.response_builder_helper(cmd_firmware,rx_spv1_frame)

        elif rx_spv1_frame.command == Def_MIFARE_COMMANDS.CHANGE_BAUD_RATE:

            cmd_change_baudrate = CmdChangeBaudrate()
            self.spv1handler.response_builder_helper(cmd_change_baudrate,rx_spv1_frame)

        else:
            print("UNKNOWN ASYNC COMMAND RESPONSE",hex(rx_spv1_frame.command))
            pass
            #custom handle rx protocol




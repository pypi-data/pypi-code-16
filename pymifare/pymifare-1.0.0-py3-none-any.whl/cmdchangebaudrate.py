from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from enum import IntEnum

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare


class EnumBaudrate(IntEnum):
    BR9600 = 0,
    BR19200 = 1
    BR38400 = 2,
    BR57600 = 3,
    BR115200 = 4,


class CmdChangeBaudrate(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdchangebaudrate)


        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdchangebaudrate
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdChangeBaudrate.PARAMS_CHANGE_BAUDRATE)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdchangebaudrate
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE()

    class PARAMS_CHANGE_BAUDRATE(ctypes.Structure):
        def __init__(self):
            self.baudrate = EnumBaudrate.BR19200
            super().__init__(baudrate=self.baudrate)


        _fields_ = [("baudrate", c_ubyte)]


    def build(self, commandParams:PARAMS_CHANGE_BAUDRATE, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





from mifaredef import *
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import STRUCT_SPV1FRAME

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare


class RESPONSE_FIRMWARE(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.firmwareString = b' '

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(firmwareString=self.firmwareString,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("firmwareString", c_char_p),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]


class CmdFirmware(CommandBaseSpv1):
    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdfirmware)

        # dll functions
        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdfirmware
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong,ctypes.c_ubyte)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdfirmware
        self.spv1_get_response_api.restype =RESPONSE_FIRMWARE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_FIRMWARE()


    def build(self, nodeAddress=0):
        txframe = self.spv1_command_build_api(self.command_instance,nodeAddress)
        return txframe

    def get_response(self):


        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.firmwareString = str_response.firmwareString

        # parse base response common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





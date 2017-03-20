import ctypes
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import STRUCT_SPV1FRAME
from mifaredef import RESPONSE_ACTIVATE

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare

class CmdActivateAll(CommandBaseSpv1):
    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdactivateall)

        # dll functions
        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdactivateall
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong,ctypes.c_ubyte)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdactivateall
        self.spv1_get_response_api.restype = RESPONSE_ACTIVATE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_ACTIVATE()


    def build(self, nodeAddress=0):
        txframe = self.spv1_command_build_api(self.command_instance,nodeAddress)
        return txframe

    def get_response(self):


        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.sak = str_response.sak
        self.response.uidLength = str_response.uidLength
        self.response.uid = str_response.uid # bytes(str_response.uid[:8])
        #self.response.uid = (ctypes.c_ubyte *8)(*str_response.uid) This is O.K

        # parse base response common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





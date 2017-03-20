from mifaredef import *
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class CmdDecrementValueBlock(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmddecrementvalueblock)

        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmddecrementvalueblock
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdDecrementValueBlock.PARAMS_DECREMENT_VALUE_BLOCK)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmddecrementvalueblock
        self.spv1_get_response_api.restype = RESPONSE_READ_WRITE_VALUE_BLOCK
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_READ_WRITE_VALUE_BLOCK()

    class PARAMS_DECREMENT_VALUE_BLOCK(PARAMS_WRITE_VALUE_BLOCK_BASE):
        def __init__(self):
            super().__init__()


    def build(self, commandParams:PARAMS_WRITE_VALUE_BLOCK_BASE, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        # Parse response - command specific
        self.response.mifareBlockNo = str_response.mifareBlockNo
        self.response.value = str_response.value

        #Parse response - common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response




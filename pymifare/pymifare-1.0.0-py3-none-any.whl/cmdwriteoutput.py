from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from pyspv1.spsc import *


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class STR_WRITE_OUTPUT_RESPONSE(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.outputStatus = 0

        #Helper members will be converted when parsing response.
        self.output1 = False
        self.output2 = False

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(outputStatus=self.outputStatus,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("outputStatus", c_ubyte),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]



class CmdWriteOutput(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdwriteoutput)

        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdwriteoutput
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdWriteOutput.STR_WRITE_OUTPUT_COMMAND_PARAMS)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdwriteoutput
        self.spv1_get_response_api.restype = STR_WRITE_OUTPUT_RESPONSE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = STR_WRITE_OUTPUT_RESPONSE()

    class STR_WRITE_OUTPUT_COMMAND_PARAMS(ctypes.Structure):
        def __init__(self):

            # Helper members will be converted when building params.
            self.output1 = False
            self.output2 = False

            super().__init__(outputStatus=0)

        _fields_ = [("outputStatus", c_ubyte)]

    def build(self, commandParams:STR_WRITE_OUTPUT_COMMAND_PARAMS, nodeAddress=0):

        outputStatus = 0
        if commandParams.output1:
            outputStatus |= 0x01
        if commandParams.output2:
            outputStatus |= 0x02
        commandParams.outputStatus = outputStatus

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.outputStatus = str_response.outputStatus

        #Parse helper members
        if self.response.outputStatus & 0x01:
            self.response.output1 = True
        else:
            self.response.output1 = False

        if self.response.outputStatus & 0x02:
            self.response.output2 = True
        else:
            self.response.output2 = False

        #Parse response - common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response




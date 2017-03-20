from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from pyspv1.spsc import *

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class RESPONSE_READ_INPUT(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.inputStatus = 0

        #Helper members will be converted when parsing response.
        self.input1 = False
        self.input2 = False

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(inputStatus=self.inputStatus,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("inputStatus", c_ubyte),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]



class CmdReadInput(CommandBaseSpv1):
    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdreadinput)

        # dll functions
        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdreadinput
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong,ctypes.c_ubyte)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdreadinput
        self.spv1_get_response_api.restype = RESPONSE_READ_INPUT
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_READ_INPUT()


    def build(self, nodeAddress=0):
        txframe = self.spv1_command_build_api(self.command_instance,nodeAddress)
        return txframe

    def get_response(self):


        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.inputStatus = str_response.inputStatus

        #Parse helper members
        if self.response.inputStatus & 0x01:
            self.response.input1 = True
        else:
            self.response.input1 = False

        if self.response.inputStatus & 0x02:
            self.response.input2 = True
        else:
            self.response.input2 = False


        # parse base response common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





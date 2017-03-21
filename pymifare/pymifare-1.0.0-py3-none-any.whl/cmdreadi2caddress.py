from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from pyspv1.spsc import *

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class RESPONSE_READ_I2C_ADDRESS(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.i2cAddress = 0


        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(i2cAddress=self.i2cAddress,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("i2cAddress", c_ubyte),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]



class CmdReadI2cAddress(CommandBaseSpv1):
    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdreadi2caddress)

        # dll functions
        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdreadi2caddress
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong,ctypes.c_ubyte)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdreadi2caddress
        self.spv1_get_response_api.restype = RESPONSE_READ_I2C_ADDRESS
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_READ_I2C_ADDRESS()


    def build(self, nodeAddress=0):
        txframe = self.spv1_command_build_api(self.command_instance,nodeAddress)
        return txframe

    def get_response(self):


        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.i2cAddress = str_response.i2cAddress

        # parse base response common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





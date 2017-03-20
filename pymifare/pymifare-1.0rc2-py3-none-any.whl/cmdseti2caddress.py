from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from pyspv1.spsc import *


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class CmdSetI2cAddress(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdseti2caddress)


        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdseti2caddress
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdSetI2cAddress.PARAMS_SET_I2C_ADDRESS)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdseti2caddress
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE()

    class PARAMS_SET_I2C_ADDRESS(ctypes.Structure):
        def __init__(self):
            self.i2cAddress = 0
            super().__init__(i2cAddress=self.i2cAddress)


        _fields_ = [("i2cAddress", c_ubyte)]


    def build(self, commandParams:PARAMS_SET_I2C_ADDRESS, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





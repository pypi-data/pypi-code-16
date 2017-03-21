from mifaredef import *
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class CmdStoreKey(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdstorekey)


        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdstorekey
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdStoreKey.PARAMS_STORE_KEY)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdstorekey
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE() #CmdAuthenticate.Response()

    class PARAMS_STORE_KEY(ctypes.Structure):
        def __init__(self):
            self.keyType = EnumKeyType.ENUM_KEY_TYPE_A
            self.internalReaderMemoryBlockNo = 0;
            self.key = (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
            super().__init__(keyType=self.keyType,
                             internalReaderMemoryBlockNo = self.internalReaderMemoryBlockNo,
                             key = self.key)

        _fields_ = [("keyType", c_int),
                    ("internalReaderMemoryBlockNo", c_ubyte),
                    ("key", ctypes.c_ubyte * 6)]



    def build(self, commandParams:PARAMS_STORE_KEY, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





from mifaredef import *
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import STRUCT_SPV1FRAME
from pyspv1.spv1 import RESPONSE_BASE

from enum import IntEnum

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class EnumAuthenticationSource(IntEnum):
    ENUM_MIFARE_DEFAULT = 0,
    ENUM_PROVIDED_KEY = 1
    ENUM_INTERNAL_EEPROM = 2,



class CmdAuthenticate(CommandBaseSpv1):

    def __init__(self): # logcallback = DefaultSpscLogger.print_log):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdauthenticate)

        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdauthenticate
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdAuthenticate.PARAMS_AUTHENTICATE)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdauthenticate
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE() #CmdAuthenticate.Response()

    class PARAMS_AUTHENTICATE(ctypes.Structure):
        def __init__(self):
            self.authenticationSource = EnumAuthenticationSource.ENUM_PROVIDED_KEY  # .MIFARE_DEFAULT
            self.keyType = EnumKeyType.ENUM_KEY_TYPE_A
            self.mifareBlockNo = 2;
            self.internalReaderMemoryBlockNo = 0;
            self.keys = (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
            super().__init__(authenticationSource=self.authenticationSource,
                             mifareBlockNo=self.mifareBlockNo,
                             internalReaderMemoryBlockNo = self.internalReaderMemoryBlockNo,
                             keyType=self.keyType,
                             keys = self.keys)

        _fields_ = [("authenticationSource", c_int),
                    ("keyType", c_int),
                    ("mifareBlockNo", c_ubyte),
                    ("internalReaderMemoryBlockNo", c_ubyte),
                    ("keys", ctypes.c_ubyte * 6)]


    def build(self, commandParams:PARAMS_AUTHENTICATE, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





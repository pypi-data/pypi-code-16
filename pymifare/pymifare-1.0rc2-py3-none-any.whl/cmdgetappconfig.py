from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import STRUCT_SPV1FRAME
from pyspv1.spsc import *

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare


class RESPONSE_APP_CONFIG (ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        # we dont want to reflect hardwareConfig and autoModeConfiguration to users.
        # because helper members construct these values.
        #self.hardwareConfig = 0
        self.serialNodeAddress = 0
        #self.autoModeConfiguration = 0
        self.asciiHeader = 0
        self.asciiFooter = 0
        self.i2cAddress = 0x42
        self.reserved = (0,0)

        #  Helper members will be converted when parsing response or building command params
        #  The following members create hardwareConfig and autoModeConfiguration structure members
        self.autoModeEnabled = False
        self.autoBeepOnSelect = False
        self.seekForTagOnStartUp = False
        self.sendFirmwareVersionOnStartUp = False
        self.rs485Enabled = False
        self.rsS485PollingMode = False
        self.i2cEnabled = False
        self.autoModeOutputASCII = False #else protocol
        self.autoModeSendCRLF = False


        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(hardwareConfig=0,
                         serialNodeAddress=self.serialNodeAddress,
                         autoModeConfiguration=0,
                         asciiHeader=self.asciiHeader,
                         asciiFooter=self.asciiFooter,
                         i2cAddress=self.i2cAddress,
                         reserved=self.reserved,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("hardwareConfig", c_ubyte),
                ("serialNodeAddress", c_ubyte),
                ("autoModeConfiguration", c_ubyte),
                ("asciiHeader", c_ubyte),
                ("asciiFooter", c_ubyte),
                ("i2cAddress", c_ubyte),
                ("reserved", c_ubyte*2),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]


class CmdGetAppConfig(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdgetappconfig)

        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdgetappconfig
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdgetappconfig
        self.spv1_get_response_api.restype = RESPONSE_APP_CONFIG
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_APP_CONFIG()

    def build(self, nodeAddress=0):

        txframe = self.spv1_command_build_api(self.command_instance,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.hardwareConfig = str_response.hardwareConfig
        self.response.serialNodeAddress = str_response.serialNodeAddress
        self.response.autoModeConfiguration = str_response.autoModeConfiguration
        self.response.asciiHeader = str_response.asciiHeader
        self.response.asciiFooter = str_response.asciiFooter
        self.response.i2cAddress = str_response.i2cAddress
        self.response.reserved = str_response.reserved

        #Parse helper members
        #Parse hardwareConfig byte
        if self.response.hardwareConfig & 0x01:
            self.response.autoModeEnabled = True
        else:
            self.response.autoModeEnabled = False

        if self.response.hardwareConfig & 0x02:
            self.response.sendFirmwareVersionOnStartUp = True
        else:
            self.response.sendFirmwareVersionOnStartUp = False

        if self.response.hardwareConfig & 0x04:
            self.response.seekForTagOnStartUp = True
        else:
            self.response.seekForTagOnStartUp = False

        if self.response.hardwareConfig & 0x08:
            self.response.rs485Enabled = True
        else:
            self.response.rs485Enabled = False

        if self.response.hardwareConfig & 0x10:
            self.response.rsS485PollingMode = True
        else:
            self.response.rsS485PollingMode = False

        if self.response.hardwareConfig & 0x20:
            self.response.i2cEnabled = True
        else:
            self.response.i2cEnabled = False

        #Parse autoModeConfiguration byte
        if self.response.autoModeConfiguration & 0x01:
            self.response.autoModeOutputASCII = True
        else:
            self.response.autoModeOutputASCII = False

        if self.response.autoModeConfiguration & 0x02:
            self.response.autoModeSendCRLF = True
        else:
            self.response.autoModeSendCRLF = False

        if self.response.autoModeConfiguration & 0x04:
            self.response.autoBeepOnSelect = True
        else:
            self.response.autoBeepOnSelect = False

        #Parse response - common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response




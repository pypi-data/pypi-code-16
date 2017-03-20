from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from pyspv1.spsc import *
from cmdgetappconfig import RESPONSE_APP_CONFIG


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class CmdSetAppConfig(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdsetappconfig)

        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdsetappconfig
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdSetAppConfig.PARAMS_SET_APP_CONFIG)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdsetappconfig
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE()

    class PARAMS_SET_APP_CONFIG(ctypes.Structure):
        def __init__(self):
            # Command specific Response members:
            # we dont want to reflect hardwareConfig and autoModeConfiguration to users.
            # because helper members construct these values.
            # self.hardwareConfig = 0
            self.serialNodeAddress = 0
            # self.autoModeConfiguration = 0
            self.asciiHeader = 0
            self.asciiFooter = 0
            self.i2cAddress = 0x42
            self.reserved = (0, 0)

            #  Helper members will be converted when parsing response or building command params
            #  The following members create hardwareConfig and autoModeConfiguration structure members
            self.autoModeEnabled = False
            self.autoBeepOnSelect = False
            self.seekForTagOnStartUp = False
            self.sendFirmwareVersionOnStartUp = False
            self.rs485Enabled = False
            self.rsS485PollingMode = False
            self.i2cEnabled = False
            self.autoModeOutputASCII = False  # else protocol
            self.autoModeSendCRLF = False

            super().__init__(hardwareConfig=0,
                             serialNodeAddress=self.serialNodeAddress,
                             autoModeConfiguration=0,
                             asciiHeader=self.asciiHeader,
                             asciiFooter=self.asciiFooter,
                             i2cAddress=self.i2cAddress,
                             reserved=self.reserved)

        _fields_ = [("hardwareConfig", c_ubyte),
                    ("serialNodeAddress", c_ubyte),
                    ("autoModeConfiguration", c_ubyte),
                    ("asciiHeader", c_ubyte),
                    ("asciiFooter", c_ubyte),
                    ("i2cAddress", c_ubyte),
                    ("reserved", c_ubyte * 2)]

        def bind(self,appConfigResponse:RESPONSE_APP_CONFIG):
            #hardwareConfig
            self.autoModeEnabled = appConfigResponse.autoModeEnabled
            self.sendFirmwareVersionOnStartUp = appConfigResponse.sendFirmwareVersionOnStartUp
            self.seekForTagOnStartUp = appConfigResponse.seekForTagOnStartUp
            self.rs485Enabled = appConfigResponse.rs485Enabled
            self.rsS485PollingMode = appConfigResponse.rsS485PollingMode
            self.i2cEnabled = appConfigResponse.i2cEnabled

            #autoModeConfiguration
            self.autoModeOutputASCII = appConfigResponse.autoModeOutputASCII
            self.autoModeSendCRLF = appConfigResponse.autoModeSendCRLF
            self.autoBeepOnSelect = appConfigResponse.autoBeepOnSelect

            self.serialNodeAddress = appConfigResponse.serialNodeAddress
            self.asciiHeader = appConfigResponse.asciiHeader
            self.asciiFooter = appConfigResponse.asciiFooter
            self.i2cAddress = appConfigResponse.i2cAddress
            self.reserved = appConfigResponse.reserved



    def build(self, commandParams = PARAMS_SET_APP_CONFIG, nodeAddress=0):

        # Helper members to actual structure value ->
        # hardwareConfig
        commandParams.hardwareConfig = 0

        if commandParams.autoModeEnabled:
            commandParams.hardwareConfig |= 0x01

        if commandParams.sendFirmwareVersionOnStartUp:
            commandParams.hardwareConfig |= 0x02

        if commandParams.seekForTagOnStartUp:
            commandParams.hardwareConfig |= 0x04

        if commandParams.rs485Enabled:
            commandParams.hardwareConfig |= 0x08

        if commandParams.rsS485PollingMode:
            commandParams.hardwareConfig |= 0x10

        if commandParams.i2cEnabled:
            commandParams.hardwareConfig |= 0x20


        #autoModeConfiguration byte
        commandParams.autoModeConfiguration =0
        if commandParams.autoModeOutputASCII:
            commandParams.autoModeConfiguration |= 0x01

        if commandParams.autoModeSendCRLF:
            commandParams.autoModeConfiguration |= 0x02

        if commandParams.autoBeepOnSelect:
            commandParams.autoModeConfiguration |= 0x04


        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse response - common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response




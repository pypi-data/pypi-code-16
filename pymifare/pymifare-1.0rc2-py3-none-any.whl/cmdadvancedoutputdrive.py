from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *
from enum import IntEnum

from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare


class EnumOutputState(IntEnum):
    OFF = 0,
    ON = 1
    ADVANCED = 2,


class STRUCT_OUTPUT_CONFIG(ctypes.Structure):
    def __init__(self,outputId=0,outputState:EnumOutputState=EnumOutputState.OFF,onTime=0,offTime=0,repeatCount=0):
        self.outputId = outputId
        self.outputState = outputState
        self.repeatCount = repeatCount
        self.onTime = onTime
        self.offTime = offTime

        super().__init__(outputId=self.outputId,
                         outputState = self.outputState,
                         repeatCount = self.repeatCount,
                         onTime = self.onTime,
                         offTime = self.offTime)

    _fields_ = [("outputId", c_ubyte),
                ("outputState", c_ubyte),
                ("repeatCount", c_ubyte),
                ("onTime", c_uint),
                ("offTime", c_uint)]


class CmdAdvancedOutputDrive(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdadvancedoutputdrive)


        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdadvancedoutputdrive
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdAdvancedOutputDrive.PARAMS_ADVANCED_OUTPUT_DRIVE)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdadvancedoutputdrive
        self.spv1_get_response_api.restype = RESPONSE_BASE
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_BASE() #CmdAuthenticate.Response()

    class PARAMS_ADVANCED_OUTPUT_DRIVE(ctypes.Structure):
        def __init__(self):
            self.soundType = 0
            # self.outputs can be used as helper. User can create new output by appending to the python list instead of
            # direct access by index between [0:5] to outputlist(structure member)
            self.outputs =[]
            #self.outputs = [STR_OUTPUT_CONFIG() for i in range (6)]
            # Following is O.K. Autocomplete can find members. But we are using self.outputs as helper.
            #self.outputList = (STR_OUTPUT_CONFIG(),
            #                   STR_OUTPUT_CONFIG(),
            #                   STR_OUTPUT_CONFIG(),
            #                   STR_OUTPUT_CONFIG(),
            #                   STR_OUTPUT_CONFIG(),
            #                   STR_OUTPUT_CONFIG())
            self.outputlist = () #(STR_OUTPUT_CONFIG*6)()  #This is OK but autocomplete cannot find memebrs
            # () This(only paranthesis) is O.K but autocomplete cannot find members
            # OK-> STR_OUTPUT_CONFIG(),STR_OUTPUT_CONFIG(),STR_OUTPUT_CONFIG(),STR_OUTPUT_CONFIG(),STR_OUTPUT_CONFIG(),STR_OUTPUT_CONFIG())
            super().__init__(soundType=self.soundType)
                             #outputList = self.outputList)


        _fields_ = [("soundType", c_ubyte),
                    ("outputList", STRUCT_OUTPUT_CONFIG * 6)]


    def build(self, commandParams:PARAMS_ADVANCED_OUTPUT_DRIVE, nodeAddress=0):

        for i in range(len(commandParams.outputs)):
            if i > 5:
                break
            commandParams.outputList[i] = commandParams.outputs[i]

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        #Parse structure response(c type) to Python Response (python class)
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response





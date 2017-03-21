from mifaredef import *
from pyspv1.commandbasespv1 import CommandBaseSpv1
from pyspv1.spv1 import *


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare




class CmdWriteDataBlock(CommandBaseSpv1):

    def __init__(self):
        super().__init__(spv1handler, spv1handler.dll.spv1_create_cmdwriteblock)

        self.checkSectorTrailer = True
        self.spv1_command_build_api = spv1handler.dll.spv1_build_cmdwriteblock
        self.spv1_command_build_api.restype = STRUCT_SPV1FRAME
        self.spv1_command_build_api.argtypes = (ctypes.c_ulong, CmdWriteDataBlock.PARAMS_WRITE_BLOCK)

        self.spv1_get_response_api = spv1handler.dll.spv1_get_response_cmdreadblock
        self.spv1_get_response_api.restype = RESPONSE_READ_WRITE_BLOCK
        self.spv1_get_response_api.argtypes = (ctypes.c_ulong,)

        self.response = RESPONSE_READ_WRITE_BLOCK()

    class PARAMS_WRITE_BLOCK(ctypes.Structure):
        def __init__(self):
            self.mifareBlockNo = 0;
            self.blockData = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

            super().__init__(mifareBlockNo=self.mifareBlockNo,
                             blockData=self.blockData)

        _fields_ = [("mifareBlockNo", c_ubyte),
                    ("blockData", ctypes.c_ubyte * 16)]

    def build(self, commandParams:PARAMS_WRITE_BLOCK, nodeAddress=0):

        if self.checkSectorTrailer:
            if IsSectorTrailer(commandParams.mifareBlockNo):
                raise Exception('Mifare Block No:' + str(commandParams.mifareBlockNo) +  ' is a sector trailer block, not a data block!')

        txframe = self.spv1_command_build_api(self.command_instance,commandParams,nodeAddress)
        return txframe

    def get_response(self):

        str_response = self.spv1_get_response_api(self.command_instance)

        # Parse response - command specific
        self.response.mifareBlockNo = str_response.mifareBlockNo
        self.response.blockData = str_response.blockData

        #Parse response - common for all commands
        self.response.responseErrorcode = str_response.responseErrorcode
        self.response.responseMessage = str_response.responseMessage
        self.response.f = str_response.f

        return self.response




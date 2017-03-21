from cmdwritedatablock import *


from globalvar import spv1handler
# do not link to mifare.py here. It creates a circular dependency and we get ImportError
# mifare > MifareAsyncHandler > cmdActivateAll/(and some other async commands found in MifareAsyncHandler) > mifare



class CmdWriteSectorTrailerBlock(CmdWriteDataBlock):

    def __init__(self):
        super().__init__()


    class PARAMS_SECTOR_TRAILER():
        def __init__(self):
            self.sectorNo = 0
            self.keyA = (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
            self.keyB = (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
            self.accessBits = (0xFF, 0x07, 0x80)


    #Overriding build of Baseclass(CmdWriteDataBlock)
    def build(self, commandParams:PARAMS_SECTOR_TRAILER, nodeAddress=0):

        if commandParams.sectorNo<0 or commandParams.sectorNo>39:
            raise Exception('Sector no can be between [0 - 39]')

        #if IsSectorTrailer(commandParams.mifareBlockNo):
        #    raise Exception('Mifare Block No:' + str(commandParams.mifareBlockNo) +  ' is a sector trailer block, not a data block!')
        write_block_command_params = CmdWriteDataBlock.PARAMS_WRITE_BLOCK()
        write_block_command_params.mifareBlockNo= GetConfigurationBlockNo(commandParams.sectorNo)
        for i in range(6):
            write_block_command_params.blockData[i]=commandParams.keyA[i]

        for i in range(3):
            write_block_command_params.blockData[i+6]=commandParams.accessBits[i]

        write_block_command_params.blockData[9] = 0x69  # User Data

        for i in range(6):
            write_block_command_params.blockData[i+10]=commandParams.keyB[i]

        self.checkSectorTrailer = False
        txframe = super().build(write_block_command_params,nodeAddress)
        return txframe



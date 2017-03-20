import ctypes
from ctypes import *
from enum import IntEnum

from pyspv1.spv1dll import Spv1Dll # This is necessary to add path for pyspv1 project even we dont use it here.import
from pyspv1.spv1 import STRUCT_SPV1FRAME
from pyspv1.spsc  import Def_SPSCERR

class Def_MIFARE_COMMANDS:
    RESET = 0x80
    FIRMWARE = 0x81
    SEEK_FOR_TAG = 0x82
    ACTIVATE_ALL = 0x83
    CHANGE_BAUD_RATE = 0x94

class RESPONSE_READ_WRITE_BLOCK(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.mifareBlockNo = 0
        self.blockData = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(mifareBlockNo=self.mifareBlockNo,
                         blockData = self.blockData,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("mifareBlockNo", c_ubyte),
                ("blockData", ctypes.c_ubyte * 16),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]

class RESPONSE_READ_WRITE_VALUE_BLOCK(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.mifareBlockNo = 0
        self.value = 0

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(mifareBlockNo=self.mifareBlockNo,
                         value = self.value,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("mifareBlockNo", c_ubyte),
                ("value", ctypes.c_long),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]

class RESPONSE_ACTIVATE(ctypes.Structure):
    def __init__(self):
        # Command specific Response members:
        self.sak = 0
        self.uidLength = 0
        self.uid = (0, 0, 0, 0, 0, 0, 0, 0)

        # Base members for all command responses.
        self.responseErrorcode = Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.responseMessage = b''
        self.f = STRUCT_SPV1FRAME()

        super().__init__(sak=self.sak,
                         uidLength = self.uidLength,
                         uid = self.uid,
                         responseErrorcode=self.responseErrorcode,
                         responseMessage=self.responseMessage,
                         f=self.f)

    _fields_ = [("sak", c_ubyte),
                ("uidLength", c_ubyte),
                ("uid", ctypes.c_ubyte * 8),
                ("responseErrorcode", c_ubyte),
                ("responseMessage", c_char_p),
                ("f", STRUCT_SPV1FRAME)]

class PARAMS_WRITE_VALUE_BLOCK_BASE(ctypes.Structure):
    def __init__(self):
        self.mifareBlockNo = 0;
        self.value = 0;
        super().__init__(mifareBlockNo=self.mifareBlockNo,
                         value=self.value)

    _fields_ = [("mifareBlockNo", c_ubyte),
                ("value", c_long)]

class PARAMS_MIFARE_BLOCK_NO_BASE(ctypes.Structure):
    def __init__(self):
        self.mifareBlockNo = 0;
        super().__init__(mifareBlockNo=self.mifareBlockNo)

    _fields_ = [("mifareBlockNo", c_ubyte)]

class EnumKeyType(IntEnum):
    ENUM_KEY_TYPE_A = 0,
    ENUM_KEY_TYPE_B = 1,



""" Alternate Way
class ACTIVATE_ALL_RESPONSE(STR_BASE_RESPONSE):
    def __init__(self):
        super().__init__()
        self.sak = 0
        self.uidLength = 0
        self.uid = (0,0,0,0,0,0,0,0)

    class STRUCTURE(ctypes.Structure):
        _fields_ = [("sak", c_ubyte),
                    ("uidLength", c_ubyte),
                    ("uid", ctypes.c_ubyte * 8)
                    ("responseErrorcode", c_ubyte),
                    ("responseMessage", c_char_p),
                    ("f", STR_SPV1FRAME)]
"""



def  IsSectorTrailer(mifareBlockNo)-> bool:
    if (mifareBlockNo<128):
        if (mifareBlockNo % 4) == 3:
            return True
    else:
        #This can be Mifare 4K
        mifareBlockNo -= 128
        if (mifareBlockNo % 16)== 15:
            return True

    return False


def GetConfigurationBlockNo(sectorNo)->int:
    blockNo = 0
    if sectorNo < 32:
        blockNo = (sectorNo*4) + 3
    elif sectorNo < 40:
        sectorNo -=32
        blockNo = 128
        blockNo += (sectorNo*16)+15

    blockNo = blockNo & 0xFF
    return blockNo



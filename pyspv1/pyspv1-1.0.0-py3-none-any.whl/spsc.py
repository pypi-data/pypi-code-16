import ctypes
from ctypes import *
from enum import IntEnum


"""Common Interfaces for spsc dll objects and python"""

class Def_SPSCERR:
    SUCCESS = 0
    FAIL = 1
    RESPONSE_FRAME_LENGTH_ERROR = 2
    RESPONSE_HEADER_MISMATCH = 3
    RESPONSE_DATALENGTH_MISMATCH = 4
    CHECKSUM_MISMATCH = 5
    TIMEOUT = 6
    UNKNOWN_RESPONSE = 7
    RESPONSE_NOT_AVAILABLE = 8


class STR_LOG(ctypes.Structure):
    _fields_ = [("logtype",c_int),
                ("returntype", c_int),
                ("commandId", c_int),
                ("responseErrorCode", c_int),
                ("paddress", c_char_p),
                ("pinfo", c_char_p),
                ("pcommandName", c_char_p),
                ("pframe", c_char_p),
                ("pdescription", c_char_p),
                ("pparameters", c_char_p)]



# log = (STR_LOG * 1)() #if argument is used as pointer
# structure arguments can be given by parameter name as follows:
# test = STR_TEST(True,myint=2,buffer=array)
# txframe = STR_SPV1FRAME(frameBufferLength=4, frameBuffer=array)

class EnumLogFilter(IntEnum):
    NONE = 0,
    ALL = 1,
    ONLY_FAILURES = 2



class EnumLogType(IntEnum):
    UDP_TX = 0,
    UDP_RX = 1,
    UDP_RX_ASYNC = 2,
    UDP_RX_OK_RESPONSE_FAIL = 3,
    TCP_TX = 4,
    TCP_RX = 5,
    TCP_RX_ASYNC = 6,
    TCP_RX_OK_RESPONSE_FAIL = 7,
    COM_TX = 8,
    COM_RX = 9,
    COM_RX_ASYNC = 10,
    COM_RX_OK_RESPONSE_FAIL = 11,
    INFO = 12,
    ADDITIONAL_INFO = 13,
    FAIL = 14

class EnumReturnType(IntEnum):
    SUCCESS = 0,
    FAIL = 1,
    TIMEOUT =2,
    RX_OK_RESPONSE_FAIL = 3,
    RETURN_NOT_AVAILABLE = 4

#class EnumEmitLogOption(Enum):
#    DONT_EMIT_LOG = 0   #0 False
#    EMIT_LOG = 1,        #1 True

class LogInfo:

    def __init__(self):
        self.clearLog()

    def clearLog(self):
        self.logtype = EnumLogType(EnumLogType.INFO)
        self.returntype = EnumReturnType(EnumReturnType.RETURN_NOT_AVAILABLE)
        self.commandID =0
        self.responseErrorCode =Def_SPSCERR.RESPONSE_NOT_AVAILABLE
        self.address = ""
        self.info = ""
        self.commandName =""
        self.frame = ""
        self.description =""
        self.parameters = ""

    def buildLog(self,log:STR_LOG):
        self.logtype = log.logtype
        self.returntype = log.returntype;
        self.commandID = log.commandId
        self.responseErrorCode = log.responseErrorCode
        self.address = log.paddress.decode("utf-8")
        self.info = log.pinfo.decode("utf-8")
        self.commandName = log.pcommandName.decode("utf-8")
        self.frame = log.pframe.decode("utf-8")
        self.description = log.pdescription.decode("ascii",errors='ignore') # For example; 0xFF cannot be decoded.
        #self.description = log.pdescription
        self.parameters = log.pparameters.decode("utf-8")
        #if self.logType == EnumLogType.FAIL:
        #    print(self.logType,"FAIL")


class DefaultSpscLogger():
    #print("DefaultSpscLogger created")
    logcounter = 0
    vertical_log = False
    log_filter = EnumLogFilter.ALL

    def __init__(self): #,vertical_log=False,log_filter = EnumLogFilter.ALL):
        pass
        #is set outside by Spv1dll:initialize()
        #DefaultSpscLogger.vertical_log = vertical_log
        #DefaultSpscLogger.log_filter = log_filter


    @staticmethod
    def indent(strval,charcolwidth) -> str:
        strval = strval.strip()
        length = len(strval)
        while length < charcolwidth:
            strval +=" "
            length +=1
        return strval

    @staticmethod
    def print_log(log: LogInfo):

        if DefaultSpscLogger.log_filter == EnumLogFilter.NONE:
            return

        if DefaultSpscLogger.log_filter == EnumLogFilter.ONLY_FAILURES:
            if log.logtype != EnumLogType.FAIL:
                return

        strlogtype="unknown"

        if log.logtype == EnumLogType.INFO:
            strlogtype = "info"
        elif log.logtype == EnumLogType.FAIL:
            strlogtype = "fail"
        elif log.logtype == EnumLogType.COM_RX_ASYNC:
            strlogtype = "com rx async <<"
        elif log.logtype == EnumLogType.COM_TX:
            strlogtype = "com tx >>"
        elif log.logtype == EnumLogType.COM_RX:
            strlogtype = "com rx <<"
        elif log.logtype == EnumLogType.COM_RX_OK_RESPONSE_FAIL:
            strlogtype = "com rx <<"

        strlogcounter = DefaultSpscLogger.indent(str(DefaultSpscLogger.logcounter), 5)
        DefaultSpscLogger.logcounter += 1

        framelength = int(len(log.frame.replace(' ','')) / 2)
        strlogtype +='('+str(framelength)+')'

        strlogtype = DefaultSpscLogger.indent(strlogtype, 24)
        straddress = DefaultSpscLogger.indent('Address:{}'.format(log.address), 24)
        #strcommand = DefaultSpscLogger.indent('Command:{}({})'.format(log.commandName, hex(log.commandID)), 32)
        strcommand = DefaultSpscLogger.indent('{}({})'.format(log.commandName, hex(log.commandID)), 32)
        strinfo = DefaultSpscLogger.indent('{}'.format(log.info), 24)
        strframe = DefaultSpscLogger.indent('{} '.format(log.frame), 64)
        #strparams =  DefaultSpscLogger.indent('Params:{} '.format(log.parametersInfoDictionary), 0)
        strparams =  DefaultSpscLogger.indent('Params:{} '.format(log.parameters), 0)
        strdesc =  DefaultSpscLogger.indent('Desc:{} '.format(log.description), 0)

        if DefaultSpscLogger.vertical_log == False:
            print(strlogcounter,strlogtype,straddress,strcommand,strinfo,strframe,'\t\t',strparams,'\t',strdesc)
        else:
            print("{counter}\t{logtpe}".format(counter=strlogcounter,logtpe=strlogtype))
            print("  Address\t:{address}".format(address=log.address))
            print("  Command\t:{command}".format(command=strcommand))
            print("  Info\t\t:{info}".format(info=strinfo))
            print("  Frame\t\t:{frame}".format(frame=strframe))
            print("  Param\t\t:{params}".format(params=log.parameters))
            print("  Desc\t\t:{desc}".format(desc=log.description))

        #print('{logtype} {address} Command:{commandName}({commandID}) \t {Info} \t Frame:{Frame} \n Params:{Parameters} \n Desc:{Description}'.format(
        #    logtype=strlogtype,
        #    address=straddress,
        #    commandName = log.CommandName,
        #    commandID = log.CommandID,
        #    Info = log.Info,
        #    Frame = log.Frame,
        #    Parameters = log.parametersInfoDictionary,
        #    Description = log.Description))

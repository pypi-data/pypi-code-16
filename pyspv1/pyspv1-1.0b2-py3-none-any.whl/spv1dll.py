import sys
import os
import ctypes
from ctypes import *

try:
    import spsc
except:
    # using relative import
    from . import spsc
    # discover path of the module and add it to the sys.path.
    path = os.path.dirname(spsc.__file__)
    sys.path.insert(0, path)
    #print("adding path",path)

from spsc import EnumLogType
from spsc import EnumLogFilter
from spsc import STR_LOG
from spsc import LogInfo
from spsc import DefaultSpscLogger
from spv1 import STRUCT_SPV1CONSTRUCTOR
from spv1 import STRUCT_SPV1FRAME
from commandbasespv1 import CommandBaseSpv1

class Spv1Dll():

    #dll = LibraryLoader(CDLL)
    #print_log = None

    #spv1_instance = None
    #spv1_api_instance_create = None
    #spv1_api_instance_release = None
    #spv1_api_free_log = None
    #spv1_api_send_command = None
    #spv1_api_process_recevied_bytes = None
    #spv1_api_async_receive_timeout = None

    #
    #spv1_api_release_command = None
    #spv1_api_response_builder = None


    #Keep references alive - not local.
    #reference_callback_log = None
    #reference_callback_async_receiver_timer_start = None
    #reference_callback_async_receiver_timer_stop = None
    #reference_callback_check_connectione_state = None
    #reference_callback_wait_for_response = None
    #reference_callback_write_buffer = None
    #reference_callback_async_rx_protocol = None

    def __init__(self):
        pass


    def initialize(self,path="",logcallback = DefaultSpscLogger.print_log,vertical_log = False,log_filter = EnumLogFilter.ALL):
        DefaultSpscLogger.vertical_log = vertical_log
        DefaultSpscLogger.log_filter = log_filter
        self.dll = ctypes.cdll.LoadLibrary(path)
        self.print_log = logcallback


        self.spv1_api_instance_create = self.dll.spv1_create_object
        self.spv1_api_instance_create.restype = ctypes.c_ulong # address of the object we will pass for every command
        self.spv1_api_instance_create.argtypes =(STRUCT_SPV1CONSTRUCTOR,)

        self.spv1_api_instance_release = self.dll.spv1_release

        self.spv1_api_free_log = self.dll.spv1_free_log
        self.spv1_api_free_log.argtypes = (ctypes.POINTER(STR_LOG),)

        self.spv1_api_send_command = self.dll.spv1_sendcommand
        self.spv1_api_send_command.restype = c_uint
        self.spv1_api_send_command.argtypes = (ctypes.c_ulong, ctypes.c_ulong, ctypes.c_bool, ctypes.c_bool, ctypes.POINTER(STR_LOG), ctypes.POINTER(STR_LOG))

        self.spv1_api_process_recevied_bytes = self.dll.spv1_processreceviedbytes
        self.spv1_api_process_recevied_bytes.restype = c_bool
        self.spv1_api_process_recevied_bytes.argtypes = (ctypes.c_ulong, ctypes.POINTER(c_ubyte), ctypes.c_int)

        self.spv1_api_async_receive_timeout = self.dll.spv1_async_receive_timeout
        self.spv1_api_async_receive_timeout.argtypes = (ctypes.c_ulong,)

        self.spv1_api_release_command = self.dll.spv1_release_command
        self.spv1_api_release_command.argtypes = (ctypes.c_ulong,)

        self.spv1_api_response_builder =  self.dll.spv1_response_builder
        self.spv1_api_response_builder.restype = ctypes.c_uint
        self.spv1_api_response_builder.argtypes = (ctypes.c_ulong, STRUCT_SPV1FRAME, ctypes.POINTER(STR_LOG))


    def create_spv1_instance(self,callback_async_receiver_timer_start,
                             callback_async_receiver_timer_stop,
                             callback_check_connection_state,
                             callback_write_buffer,
                             callback_wait_for_response,
                             callback_async_rx_protocol):


        # we need to keep reference in self.reference_callback_log variable. Otherwise it will be garbage collected
        type_callback_log = ctypes.CFUNCTYPE(None, STR_LOG)
        self.reference_callback_log = type_callback_log(self.callback_log)

        type_callback_async_receiver_timer_start = ctypes.CFUNCTYPE(None)
        self.reference_callback_async_receiver_timer_start = type_callback_async_receiver_timer_start(callback_async_receiver_timer_start)

        type_callback_async_receiver_timer_stop = ctypes.CFUNCTYPE(None)
        self.reference_callback_async_receiver_timer_stop = type_callback_async_receiver_timer_stop(callback_async_receiver_timer_stop)

        type_callback_check_connection_state = ctypes.CFUNCTYPE(c_bool)
        self.reference_callback_check_connectione_state = type_callback_check_connection_state(callback_check_connection_state)

        type_callback_write_buffer = ctypes.CFUNCTYPE(c_bool, POINTER(ctypes.c_ubyte),c_int)
        self.reference_callback_write_buffer = type_callback_write_buffer(callback_write_buffer)

        type_callback_wait_for_response = ctypes.CFUNCTYPE(c_bool)
        self.reference_callback_wait_for_response = type_callback_wait_for_response(callback_wait_for_response)

        type_callback_async_rx_protocol = ctypes.CFUNCTYPE(None, STRUCT_SPV1FRAME)
        self.reference_callback_async_rx_protocol = type_callback_async_rx_protocol(callback_async_rx_protocol)

        spv1_constructor = STRUCT_SPV1CONSTRUCTOR(callbacklog = self.reference_callback_log,
                                                  callbackcheckconnectionstate = self.reference_callback_check_connectione_state,
                                                  callbackwritebuffer = self.reference_callback_write_buffer,
                                                  callbackwaitforresponse = self.reference_callback_wait_for_response,
                                                  callbackAsyncReceiveTimerStart = self.reference_callback_async_receiver_timer_start,
                                                  callbackAsyncReceiveTimerStop = self.reference_callback_async_receiver_timer_stop,
                                                  callbackAsyncRxProtocol = self.reference_callback_async_rx_protocol,
                                                  logtypesendcommand = int(EnumLogType.COM_TX),
                                                  logtypereceiveresponse = int(EnumLogType.COM_RX),
                                                  logtypereceiveokresponsefail =  int(EnumLogType.COM_RX_OK_RESPONSE_FAIL),
                                                  logtypeasyncincoming = int(EnumLogType.COM_RX_ASYNC))

        self.spv1_instance = self.spv1_api_instance_create(spv1_constructor)

    def callback_log(self,structure_log):
        loginfo = LogInfo()
        loginfo.buildLog(structure_log)
        self.print_log(loginfo)
        # self.spv1_free_log(structure_log) releaseing resource of the log will be handled by dll


    def release_instance(self):
        self.spv1_api_instance_release(self.spv1_instance)


    def response_builder_helper(self, command:CommandBaseSpv1, rx_spv1_frame:STRUCT_SPV1FRAME,loginfo:LogInfo = LogInfo(),auto_log= True):
        spv1_rx_log = STR_LOG()
        #prx_log = (STR_LOG * 1)()
        #p = ctypes.pointer(STR_LOG)()
        #p2 = ctypes.pointer(rx_log)
        #print(p[0].pinfo)
        errCode = self.spv1_api_response_builder(command.command_instance, rx_spv1_frame,spv1_rx_log)
        response = command.get_response()
        loginfo.buildLog(spv1_rx_log)
        loginfo.logtype = EnumLogType.COM_RX_ASYNC
        self.spv1_api_free_log(spv1_rx_log)
        if auto_log:
            self.print_log(loginfo)
        #return response

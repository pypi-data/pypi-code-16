import ctypes
from abc import ABC, abstractmethod
from spv1 import STRUCT_SPV1FRAME
from spsc import STR_LOG

class CommandBaseSpv1(ABC):
    def __del__(self):
        # If command is destroyed or created new we should release dll resources before new command is created.
        # It is recommended to create only one instance of command.
        self.spv1dllinstance.spv1_api_release_command(self.command_instance)

    def __init__(self, spv1dll, spv1_create_command_instance):
        self.spv1dllinstance = spv1dll

        # reference for parant class. Parent class needs to intiailize following params.
        self.spv1_command_build_api = None
        self.spv1_get_response_api = None

        # dll functions
        spv1_api_create_command_instance = spv1_create_command_instance
        #spv1_api_create_command_instance.argtypes = ctype_arguments
        spv1_api_create_command_instance.restype = ctypes.c_ulong

        self.command_instance =  spv1_api_create_command_instance()
        #self.command_instance =  spv1_api_create_command_instance(arg_value)


    #@abstractmethod (cant be abstract because every command pay have different command parameters)
    #def build(self, nodeAddress=0):
    #    pass

    @abstractmethod
    def get_response(self):
        pass


    def response_builder(self, rx_spv1_frame:STRUCT_SPV1FRAME, rx_log:STR_LOG):
        errCode = self.spv1dllinstance.spv1_api_response_builder(self.command_instance, rx_spv1_frame, rx_log)
        print("Response Builder ErrCode",hex(errCode))
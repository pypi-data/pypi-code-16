import time
import threading
import serial
from threading import Event
from ctypes import *

from spsc import EnumLogType
from spsc import LogInfo
from spsc import STR_LOG
from commandbasespv1 import CommandBaseSpv1

class SerialCommSpv1():
    """ Spv1 Serial Communication"""

    def __init__(self, spv1dll, spv1AsyncHandler, DefaultSerialReceiveTimeOut=0.5, AsyncReceive=True):

        # Attention, do not change self.serialPort.Timeout while read attempt.
        # This will cause data not to be sent or received properly.
        self.serialPort = serial.Serial(timeout=DefaultSerialReceiveTimeOut) #timeout=0)
        self.AsyncReceive = AsyncReceive
        self.spv1dll = spv1dll
        self.is_async_threads_started = False

        #self.spv1AsyncHandler = spv1AsyncHandler

        self.print_log = self.spv1dll.print_log
        #self.LogTypeSendCommand = EnumLogType.COM_TX
        #self.LogTypeAsyncIncoming = EnumLogType.COM_RX_ASYNC
        #self.LogTypeReceiveResponse = EnumLogType.COM_RX
        #self.LogTypeReceiveOkResponseFail = EnumLogType.COM_RX_OK_RESPONSE_FAIL
        self.AsyncTimeOut =2 # keep this long. Even 1 second can cause "fragmented" received async protocol data.


        # create spv1 dll object
        self.spv1dll.create_spv1_instance(self.dll_callback_async_receiver_timer_start,
                                                               self.dll_callback_async_receiver_timer_stop,
                                                               self.dll_callback_check_connection_state,
                                                               self.dll_callback_write_buffer,
                                                               self.dll_callback_wait_for_response,
                                                               spv1AsyncHandler.dll_callback_async_rx_protocol);


        self.event_async_timeout_run = Event()
        self.event_async_timeout_cancel = Event()
        self.async_timer_thread = threading.Thread(target = self.thread_async_timer_run, kwargs={'run_event': self.event_async_timeout_run, 'cancel_event': self.event_async_timeout_cancel})


        self.polling_rx_thread_disconnect_async_event = threading.Event()
        self.polling_rx_thread =  threading.Thread(target=self.thread_polling_rx_run, kwargs={'arg1': 1, 'disconnect_event': self.polling_rx_thread_disconnect_async_event})

    def dll_callback_async_receiver_timer_start(self):
        #print("dll_callback_async_receiver_timer_start",int(round(time.time() * 1000)))
        self.event_async_timeout_run.set()
        self.event_async_timeout_cancel.clear()

    def dll_callback_async_receiver_timer_stop(self):
        #print("dll_callback_async_receiver_timer_stop",int(round(time.time() * 1000)))
        self.event_async_timeout_cancel.set()

    def dll_callback_check_connection_state(self):
        return self.serialPort.isOpen()

    def dll_callback_write_buffer(self,pbytearray,arraysize):
        bytestobesent = bytes(pbytearray[:arraysize]) # this is O.K.    <class 'bytes'>
        # array = (ctypes.c_ubyte * 4)(0x31, 0x32, 0x33, 0x34)
        #bytestobesent = pbytearray[:arraysize] # this is O.K. <class 'list'>
        #bytestobesent = (ctypes.c_ubyte *arraysize)(pbytearray[0],pbytearray[1],pbytearray[2],pbytearray[3],pbytearray[4]) #This is O.K
        #bytestobesent = (ctypes.c_ubyte *arraysize)(*pbytearray[:arraysize]) #This is O.K

        # Alternative way to receive unsgined char array to python type >
        #ctypebytearray = cast(pbytearray, POINTER(c_ubyte * arraysize))
        #bytestobesent = ctypebytearray[0][:arraysize]
        #print(type(bytestobesent))
        #print(len(bytestobesent))
        self.serialPort.write(bytestobesent)
        return True

    def dll_callback_wait_for_response(self):
        status = True
        possibleFragmented = True
        # read 5 byte for the first time; as all command responses are greater than 5
        read_byte_count = 5
        while  (possibleFragmented == True):
            # Attention! We should not configure timeout here, read/write timeout problems will occur otherwise.
            # #self.serialPort.timeout = timeout #WRONG!
            receivedbytes = self.serialPort.read(read_byte_count)

            #read 5 byte for the first time; as all command responses are greater than 5
            #reduce it to 1 byte after first iteration
            read_byte_count = 1

            if len(receivedbytes)>0:
                possibleFragmented = self.process_received_bytes(receivedbytes)
                # if possible fragmented response frame is detected we will try reading all as a second attempt(instead of 1 by 1 in the loop)
                # This is for faster receiving response to reduce iteration count.
                # Notice: read_all is independent of serial.timeout
                # However read_all can not read all available data, because it does not wait for timeout.
                # We should keep reading 1 by 1 inside the loop. that's the only way to detect timeout
                # read_all is only optional to help reading faster.
                if possibleFragmented:
                    receivedbytes = self.serialPort.read_all()
                    if len(receivedbytes)>0:
                        possibleFragmented = self.process_received_bytes(receivedbytes)

            else:
                #print("timeout")
                return False

        return True


    def thread_async_timer_run(self, run_event: Event, cancel_event:Event):
        while True:
            #while run_event.is_set():
            #if run_event.is_set():
            while run_event.wait(1):    # wait for 1 second if run event is set outside
                #print("async timer is activated")
                #print("async timer is activated", int(round(time.time() * 1000)))
                time.sleep(self.AsyncTimeOut)
                #print("async timer check", int(round(time.time() * 1000)))

                if not cancel_event.is_set():
                    # reporting Async data
                    #print("async timeout occurs")
                    #print("async timeout occurs", int(round(time.time() * 1000)))
                    self.spv1dll.spv1_api_async_receive_timeout(self.spv1dll.spv1_instance)
                    cancel_event.clear()
                else:
                    #print("async timeout is cleared/cancelled by protocol analyzer. Protocol data is received")
                    pass


                run_event.clear()

            #time.sleep(0.1)
            #print("thread sleeping")
            #self.spv1_async_receive_timeout(self.obj_spv1)
        pass


    def thread_polling_rx_run(self, arg1, disconnect_event: Event):
        while True:
            #print("thread_polling_rx_run running")
            #print(event1.is_set())
            try:
                if not disconnect_event.is_set():
                    #print("async receive listening")
                    while self.serialPort.is_open:
                        # do not change self.serialport.timeout value here! Unexpected results may occur
                        if not disconnect_event.is_set(): # Close port can set disconnect signal here, then we should not attempt reading
                            bytes = self.serialPort.read_all()
                            while len(bytes) > 0:
                                # try to collect data one at a time as much as possible
                                #print("detected",len(bytes))
                                self.process_received_bytes(bytes)
                                #time.sleep(0.05)
                                bytes = self.serialPort.read_all()
                        time.sleep(0.1)


                else:
                    #print("async receive not listenig")
                    pass

                # if serialPort.read() is used  first byte is lost if check too frequently; i.e. time.sleep(0.1)
                time.sleep(0.1)
            except Exception as e:
                #print("exception",e)
                loginfo = LogInfo()
                loginfo.logtype = EnumLogType.FAIL
                loginfo.info = 'Exception occured. Com port Error'
                loginfo.description = e.args
                self.print_log(loginfo)
                disconnect_event.set()

                #raise Exception(e)
                pass


    def open_port(self, portName: str, baudrate: int, auto_log= True, loginfo: LogInfo = LogInfo()) -> bool:
        loginfo.clearLog()
        loginfo.commandName = "OPEN PORT"
        loginfo.address = portName + ":" + str(baudrate)

        try:
            # Close the port if was opened previosly
            if (self.serialPort.is_open):
                self.polling_rx_thread_disconnect_async_event.set()
                self.serialPort.close()

            self.serialPort.port = portName
            self.serialPort.baudrate = baudrate

            self.serialPort.open()

            if self.AsyncReceive:
                self.polling_rx_thread_disconnect_async_event.clear()
                if self.is_async_threads_started == False:
                    self.polling_rx_thread.start()
                    self.async_timer_thread.start()
                    self.is_async_threads_started = True

            loginfo.logtype = EnumLogType.INFO
            loginfo.info = "OK"
        except Exception as msg:
            loginfo.logtype = EnumLogType.FAIL
            loginfo.info = msg;
        finally:
            if auto_log:
                self.print_log(loginfo)
            return self.serialPort.is_open


    def close_port(self,auto_log= True,loginfo: LogInfo = LogInfo()):
        loginfo.clearLog()
        try:
            if self.serialPort.is_open:
                loginfo.address = self.serialPort.port + ":" + str(self.serialPort.baudrate)
                self.polling_rx_thread_disconnect_async_event.set()
                self.serialPort.close()
                # Notice that if thread started previosly will remain running.
                loginfo.commandName = "CLOSE PORT"
                loginfo.logtype = EnumLogType.INFO
                loginfo.info = "OK"
        except Exception as msg:
            loginfo.logtype = EnumLogType.FAIL
            loginfo.info = msg;
        finally:
            if auto_log:
                self.print_log(loginfo)


    #def send_command(self, txframe, auto_log= True, txloginfo = LogInfo(), rxloginfo=LogInfo()):
    def send_command(self, command:CommandBaseSpv1, wait_response = True,auto_log= True, txloginfo = LogInfo(), rxloginfo=LogInfo()):
        str_txlog = STR_LOG()
        str_rxlog = STR_LOG()

        # stop async listening
        if self.AsyncReceive:
            self.polling_rx_thread_disconnect_async_event.set()
        #self.serialPort.read_all()
        #self.serialPort.cancel_read()
        #self.serialPort.flush()


        # call dll send command. Resources must be released.
        #errCode =  self.spv1dll.sendcommand(self.obj_spv1,command.dll_obj_reference,True, auto_log, str_txlog, str_rxlog)
        errCode =  self.spv1dll.spv1_api_send_command(self.spv1dll.spv1_instance, command.command_instance, wait_response, auto_log, str_txlog, str_rxlog)
        command.get_response()
        self.spv1dll.spv1_api_free_log(str_rxlog)
        self.spv1dll.spv1_api_free_log(str_txlog)

        # enable async listening
        if self.AsyncReceive:
            self.polling_rx_thread_disconnect_async_event.clear()

        return errCode


    def process_received_bytes(self,receivedbytes):
        #print(int(round(time.time() * 1000)))
        array_type =  (c_ubyte * len(receivedbytes))
        carray = array_type(*receivedbytes)
        return  self.spv1dll.spv1_api_process_recevied_bytes(self.spv1dll.spv1_instance, carray, len(receivedbytes))
        #return   self.spv1_processreceviedbytes(self.obj_spv1,carray,len(receivedbytes))

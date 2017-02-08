#!/usr/bin/env python

__author__ = "Tao Yang"

import serial
import time
import sys

print "\r\n==>A small tool for serial port debug usage...\r\n"

# The serial port configuration
def HexShow(argv):
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        result += hhex+''
    return result

def main(argv):
    if len(sys.argv) < 6:
        print "usage:\r\n"
        print "SerialTool baudrate databits parity stopbits [tx data type:string or hex] [rx data type:string or hex]\r\n"
        print "example:SerialTool /dev/ttyUSB0 115200 8 N 1 hex hex\r\n"
        exit()
    ser = serial.Serial(
            port = sys.argv[1],
            baudrate = sys.argv[2],
            bytesize = int(sys.argv[3]),
            parity = sys.argv[4],
            stopbits = int(sys.argv[5]),
            timeout = 0.5,
            xonxoff = None,
            rtscts = None,
            interCharTimeout = None
        )
    print ser.portstr
    ser.isOpen()

    try:
        while 1 :        
            RecvData = ''
            time.sleep(1)    
            while ser.inWaiting() > 0 :
                RecvData += ser.read(1)
            if RecvData != '':
                if len(sys.argv) > 7 and sys.argv[7] == 'hex':
                    RecvData = HexShow(RecvData)
                    print "<<" + RecvData
                elif len(sys.argv) > 7 and sys.argv[7] == 'string':
                    print "<<" + RecvData
                else:
                    print "<<" + RecvData

            InPut = raw_input(">>")
            if InPut == 'exit':
                ser.close()
                exit()
            else:
                #string or hex data InPut
                if len(sys.argv) > 6 and sys.argv[6] == 'hex':
                    ser.write(InPut.decode("hex"))
                elif len(sys.argv) > 6 and sys.argv[6] == 'string':
                    ser.write(InPut + "\r\n")
                else:
                    ser.write(InPut + "\r\n")
    finally:
        ser.close()
    #    exit()

if __name__ == "__main__":
    main(sys.argv[1:])

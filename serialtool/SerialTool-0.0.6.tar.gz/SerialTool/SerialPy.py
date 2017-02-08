#!/usr/bin/env python

__author__ = "Tao Yang"

import serial
import time
import sys

print "\r\nA small tool for serial port debug usage...\n"
print "-----------------\n"
# The serial port configuration
def HexShow(argv):
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        result += hhex+''
    return result

def main():
    if len(sys.argv) < 6:
        print "usage:\n"
        print "====\n"
        print "SerialTool com baudrate databits parity stopbits [TX data type] [RX data type]\n"
        print "|_com: the serial port device name\n"
        print "|_baudrate: any standard baudrate, such as 9600, 115200, etc\n"
        print "|_databits: 5,6,7,8\n"
        print "|_parity: N,E\n"
        print "|_stopbits: 1,1.5,2\n"
        print "|_TX data types: string or hex, default is string if this parameter is null\n"
        print "|_RX data types: string or hex, default is string if this parameter is null\n"
        print "simple usage example:\n"
        print "====\n"
        print "SerialTool /dev/ttyUSB0 115200 8 N 1 hex hex\n"
        print "\r\nCONTACT\r\n"
        print "====\n"
        print "Project main page: https://pypi.python.org/pypi/SerialTool\n"
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
        exit()

if __name__ == '__main__':
    main()

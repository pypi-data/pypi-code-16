#!/usr/bin/python
#-*- coding: utf-8 -*-

""" 
Connector to use w/ bugOne sniffer. You can use serial port, Ethernet or Mux

"""
import socket


class Serial:
    def __init__(self, device="/dev/ttyUSB0", baudrate=38400):
        import serial
        self.port = serial.Serial(device, baudrate, timeout=1)

    def close(self):
        if self.port:
            self.port.close()

    def receive(self):
        # return None on error, message data else        
        buf = self.port.read(1)
        if (len(buf) != 1):
            return None
        size = ord(buf)
        data = self.port.read(size)
        if (len(data) != size):
            return None
        checksum = ord(self.port.read())
        c = 0
        for i in data:
            c ^= ord(i)
        if checksum != c:
            return None
        else:
            return data
    
    def send(self, message):
        # send data, throw an exception if size is superior 255
        if len(message) > 255:
            raise Exception("Message is too long")
        self.port.write(chr(len(message)) + message)
        self.port.flush()

        
class TCPMux:
    def __init__(self, addr='127.0.0.1',port = 12288):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((addr,port))

    def close(self):
        self.socket.close()

    def receive(self):
        buf = self.socket.recv(1)
        if (len(buf) != 1):
            return None
        size = ord(buf)
        
        data = ''
        while 1:
            data = data + self.socket.recv(256)
            if len(data) > size:
                break

        checksum = ord(data[-1])
        data = data[0:-1]

        c = 0
        for i in data:
            c ^= ord(i)
        if checksum != c:
            return None
        else:
            return data

    def send(self,data):
        self.socket.send(data)
        
        

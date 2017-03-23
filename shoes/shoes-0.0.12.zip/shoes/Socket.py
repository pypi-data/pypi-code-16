import os
import sys
import time
import socket
import warnings
import threading

class Socket:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.raw.connect((self.ip, self.port))
    def send(self,message):
        try:
            self.raw.send(bytes(message, encoding='utf-8'))
        except:
            warnings.warn("Warning: connection tunnel has been broken. Disconnected from server.")
    def receive(self):
        try:
            data = self.raw.recv(4096).decode()
            if data == chr(402): return None
            else: return data
        except:
            warnings.warn("Warning: connection tunnel has been broken. Disconnected from server.")
            return None
    def recieve(self,conn):
        return self.receive(conn)
    def disconnect(self):
        self.raw.shutdown(2)
        self.raw.close()
    def timeout(self,n):
        try:
            self.raw.settimeout(n)
        except: raise TypeError
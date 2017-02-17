"""" Hürriyet log sistemi """
import socket
import datetime

class HurriyetLog(object):
    """ Log objesinin json formatina dondurulmesi icin kullanilir """
    def __init__(self, record):
        self.record = record

    def to_json(self):
        """ Objeyi json'a dondurur """
        return {
            "ApplicationName" : self.record.filename,
            "MethodName": self.record.funcName,
            "LogLineNumber" : self.record.lineno,
            "Date" : datetime.datetime.utcfromtimestamp(self.record.created).isoformat(),
            "Level" : self.record.levelname,
            "MachineName" : socket.gethostname().upper(),
            "Message" : self.record.msg
            }

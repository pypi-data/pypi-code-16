# coding: utf-8
from enum import Enum


#region enum
# <summary>
# コマンドモード
# </summary>
class HzVoiceCommandMode(Enum):
    Normal = 0x00       #通常
#endregion


# <summary>
# 音声入力コマンド情報クラス
# </summary>
class SpeechRecognitionCommandInfo(object):
    def __init__(self):
        self.__mode = HzVoiceCommandMode.Normal.value
        self.__ip_addr = None
        self.__port = 46100
        self.__command = None
        self.__timestamp = None

    #region アクセサ定義(コマンド情報メンバ)
    def __get_mode(self):
        return self.__mode

    def __set_mode(self, mode):
        self.__mode = mode

    def __get_ip_addr(self):
        return self.__ip_addr

    def __set_ip_addr(self, ip):
        self.__ip_addr = ip

    def __get_port(self):
        return self.__port

    def __set_port(self, port):
        self.__port = port
    
    def __get_command(self):
        return self.__command

    def __set_command(self, command):
        self.__command = command

    def __get_timestamp(self):
        return self.__timestamp

    def __set_timestamp(self, timestamp):
        self.__timestamp = timestamp
    #endregion

    #region Property
    mode = property(__get_mode, __set_mode)
    ip_addr = property(__get_ip_addr, __set_ip_addr)
    port = property(__get_port, __set_port)
    command = property(__get_command, __set_command)
    timestamp = property(__get_timestamp, __set_timestamp)
    #endregion

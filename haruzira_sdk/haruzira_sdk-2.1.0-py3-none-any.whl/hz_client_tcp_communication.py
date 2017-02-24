# coding: utf-8
import struct
from enum import Enum
import threading
import time
import socket
import datetime
import numpy as np
import haruzirasdk.hz_trace as hz_trace
import haruzirasdk.hz_encryption as hz_encryption
import haruzirasdk.hz_speech_recognition_command_info as hz_speech_recognition_command_info
import haruzirasdk.haruzira_message as haruzira_message
import haruzirasdk.msg_req_start_comm as msg_req_start_comm
import haruzirasdk.msg_ack_start_comm as msg_ack_start_comm
import haruzirasdk.msg_send_speech_data as msg_send_speech_data
import haruzirasdk.msg_ack_send_speech_data as msg_ack_send_speech_data
import haruzirasdk.msg_notify_end_comm as msg_notify_end_comm
import haruzirasdk.msg_notify_stop_comm as msg_notify_stop_comm
import haruzirasdk.msg_notify_complete_speech as msg_notify_complete_speech
import haruzirasdk.msg_send_speech_recognition_command as msg_send_speech_recognition_command
import haruzirasdk.msg_ack_send_speech_recognition_command as msg_ack_send_speech_recognition_command

#region enum
# <summary>
# Mode of Text Speech
# </summary>
class HzSpeechTextMode(Enum):
    Text = 0x00        #テキスト
    Ssml = 0x01        #SSML

# <summary>
# Priority of Speech
# </summary>
class HzSpeechLevel(Enum):
    Low = 0x00        #低い（読み上げない）
    Normal = 0x01     #通常（順次読み上げ）
    High = 0x02       #高い（割り込み読み上げ）

# <summary>
# Gender of Speecher
# </summary>
class HzSpeechGender(Enum):
    Female = 0x00        #女性
    Male = 0x01          #男性
    Neutral = 0x02       #未指定

# <summary>
# SDK language type
# </summary>
class HzSdkLangType(Enum):
    Unknown = 0x00       #不明
    DotNet = 0x01        #.Net
    Ruby = 0x02          #Ruby
    Python = 0x03        #Python
    Java = 0x04          #Java

# <summary>
# Necessity of sending Speech Completion Notice message
# </summary>
class HzSpCompletionNoticeNecessity(Enum):
    Need = 0x00          #送信必要
    NoNeed = 0x01        #送信不要
#endregion

class ClientTcpCommunication(object):

    #region 変数・定数
    __DISCONNECT_REASON_END = 0x10;              #通信終了通知送信時
    __DISCONNECT_REASON_CANCEL = 0x11            #キャンセル発生時
    __DISCONNECT_REASON_SERVER_IREGULAR = 0x12   #サーバー側でイレギュラー障害発生
    __DISCONNECT_REASON_CLIENT_IREGULAR = 0x13;  #クライアント側でイレギュラー障害発生
    __QUEUE_RECEIVED = "OK" 
    __HzTrace = hz_trace.HzTrace()

    __SDK_LANG_TYPE = HzSdkLangType.Python.value
    __VERSION = "2.1.0.0"     #SDKバージョン
    #endregion

    # <summary>
    # Construct
    # </summary>
    def __init__(self):

        #region 変数・定数
        self.__encryption = hz_encryption.Encryption()
        self.__encryption_type = hz_encryption.EncryptionType.AesCbcPkcs7.value
        #self.__encryption = None
        self.__stop_event_rcv = threading.Event()
        self.__stop_event_listener = threading.Event()

        self.__work_rcv = None     #メッセージ受信スレッド
        self.__listenTask = None   #非同期メッセージ受信メインスレッド
        self.__tcpSvr = None       #TCPServer
        self.__svr_sock = None
        self.__ackStartCommAutoResetEvent = None 
        self.__ackSendSpeechDataAutoResetEvent = None
        self.__cltSocket = None 
        self.__ServerPortNo = 46000
        self.__ServerIP = "127.0.0.1"
        self.__ReceivePort = 46100
        self.__ReqSendDataText = ""
        self.__ReqSendDataEncrypt = False
        self.__ReqSendDataEncryptKey = ""
        self.__ReqSendDataAccountName = ""
        self.__ReqSendDataPasswd = ""
        self.__ReqSendDataSpeechMode = HzSpeechTextMode.Text.value
        self.__ReqSendDataSpeechLevel = HzSpeechLevel.Normal.value
        self.__ReqSendDataSpeechLocaleId = 0x00
        self.__ReqSendDataSpeechGender = HzSpeechGender.Neutral.value
        self.__ReqSendDataSpeechAge = 25
        self.__ReqSendDataSpeechRepeat = 0
        self.__ReqSendDataCompletionNoticeNecessity = HzSpCompletionNoticeNecessity.Need.value
        self.__ReceivedDataDecryptionKey = ""
        self.__SendDataHexStr = ""
        self.__SendDataLength = 0
        self.__ReceiveStatus = 0x00
        self.__ReceiveAckTimeOut = haruzira_message.RECEIVE_TIME_OUT
        self.__SdkVersions = [int(self.__VERSION.split(".")[0]), int(self.__VERSION.split(".")[1])]      #SDKバージョン(送信用) 
        #endregion

        #region Event Handler
        #メッセージ受信時イベント定義
        self.evNotifyCompleteSpeech = None                   #読み上げ完了通知受信時イベント
        self.evNotifyMessageEvent = None                     #Exception発生時イベント（切断以外）
        self.evNotifyReceivedDisconnectEvent = None          #切断発生時イベント（サーバー側からの切断など）
        self.evNotifySendSpeechRecognitionCommand = None     #音声認識コマンド送信受信時イベント
        #endregion

    #region define accessor
    def __get_server_port(self):
        return self.__ServerPortNo

    def __set_server_port(self, value):
        self.__ServerPortNo = value

    def __get_server_ip(self):
        return self.__ServerIP

    def __set_server_ip(self, value):
        self.__ServerIP = value

    def __get_receive_port(self):
        return self.__ReceivePort

    def __set_receive_port(self, value):
        self.__ReceivePort = value

    def __get_req_send_data_text(self):
        return self.__ReqSendDataText

    def __set_req_send_data_text(self, value):
        self.__ReqSendDataText = value

    def __get_req_send_data_encrypt(self):
        return self.__ReqSendDataEncrypt

    def __set_req_send_data_encrypt(self, value):
        self.__ReqSendDataEncrypt = value

    def __get_req_send_data_encrypt_key(self):
        return self.__ReqSendDataEncryptKey

    def __set_req_send_data_encrypt_key(self, value):
        self.__ReqSendDataEncryptKey = value

    def __get_req_send_data_account_name(self):
        return self.__ReqSendDataAccountName

    def __set_req_send_data_account_name(self, value):
        self.__ReqSendDataAccountName = value

    def __get_req_send_data_passwd(self):
        return self.__ReqSendDataPasswd

    def __set_req_send_data_passwd(self, value):
        self.__ReqSendDataPasswd = value

    def __get_req_send_data_speech_mode(self):
        return self.__ReqSendDataSpeechMode

    def __set_req_send_data_speech_mode(self, value):
        self.__ReqSendDataSpeechMode = value

    def __get_req_send_data_speech_level(self):
        return self.__ReqSendDataSpeechLevel

    def __set_req_send_data_speech_level(self, value):
        self.__ReqSendDataSpeechLevel = value

    def __get_req_send_data_speech_locale_id(self):
        return self.__ReqSendDataSpeechLocaleId

    def __set_req_send_data_speech_locale_id(self, value):
        self.__ReqSendDataSpeechLocaleId = value

    def __get_req_send_data_speech_gender(self):
        return self.__ReqSendDataSpeechGender

    def __set_req_send_data_speech_gender(self, value):
        self.__ReqSendDataSpeechGender = value

    def __get_req_send_data_speech_age(self):
        return self.__ReqSendDataSpeechAge

    def __set_req_send_data_speech_age(self, value):
        self.__ReqSendDataSpeechAge = value

    def __get_req_send_data_speech_repeat(self):
        return self.__ReqSendDataSpeechRepeat

    def __set_req_send_data_speech_repeat(self, value):
        self.__ReqSendDataSpeechRepeat = value

    def __get_req_send_data_completion_notice_necessity(self):
        return self.__ReqSendDataCompletionNoticeNecessity

    def __set_req_send_data_completion_notice_necessity(self, value):
        self.__ReqSendDataCompletionNoticeNecessity = value

    def __get_received_data_decryption_key(self):
        return self.__ReceivedDataDecryptionKey

    def __set_received_data_decryption_key(self, value):
        self.__ReceivedDataDecryptionKey = value

    def __get_send_data_hex_str(self):
        return self.__SendDataHexStr

    def __get_send_data_length(self):
        return self.__SendDataLength

    def __get_receive_status(self):
        return self.__ReceiveStatus

    def __get_version(self):
        return self.__VERSION

        # <summary>
    # 応答受信時タイムアウト取得・設定
    # </summary>
    # <param name="value">タイムアウト値</param>
    def __get_receive_ack_timeout(self):
        #Get
        return self.__ReceiveAckTimeOut 

    # <summary>
    # 応答受信時タイムアウト取得・設定
    # </summary>
    # <param name="value">タイムアウト値</param>
    def __set_receive_ack_timeout(self, value):
        #Set
        if(value > haruzira_message.RECEIVE_MAX_TIME_OUT):
            self.__ReceiveAckTimeOut = haruzira_message.RECEIVE_MAX_TIME_OUT
        elif(value < haruzira_message.RECEIVE_MIN_TIME_OUT):
            self.__ReceiveAckTimeOut = haruzira_message.RECEIVE_MIN_TIME_OUT
        else:
            self.__ReceiveAckTimeOut = value
    #endregion

    #region Property
    ServerPortNo = property(__get_server_port, __set_server_port)
    ServerIP = property(__get_server_ip, __set_server_ip)
    ReceivePort = property(__get_receive_port, __set_receive_port)
    ReqSendDataText = property(__get_req_send_data_text, __set_req_send_data_text)
    ReqSendDataEncrypt = property(__get_req_send_data_encrypt, __set_req_send_data_encrypt)
    ReqSendDataEncryptKey = property(__get_req_send_data_encrypt_key, __set_req_send_data_encrypt_key)
    ReqSendDataAccountName = property(__get_req_send_data_account_name, __set_req_send_data_account_name)
    ReqSendDataPasswd = property(__get_req_send_data_passwd, __set_req_send_data_passwd)
    ReqSendDataSpeechMode = property(__get_req_send_data_speech_mode, __set_req_send_data_speech_mode)
    ReqSendDataSpeechLevel = property(__get_req_send_data_speech_level, __set_req_send_data_speech_level)
    ReqSendDataSpeechLocaleId = property(__get_req_send_data_speech_locale_id, __set_req_send_data_speech_locale_id)
    ReqSendDataSpeechGender = property(__get_req_send_data_speech_gender, __set_req_send_data_speech_gender)
    ReqSendDataSpeechAge = property(__get_req_send_data_speech_age, __set_req_send_data_speech_age)
    ReqSendDataSpeechRepeat = property(__get_req_send_data_speech_repeat, __set_req_send_data_speech_repeat)
    ReqSendDataCompletionNoticeNecessity = property(__get_req_send_data_completion_notice_necessity, __set_req_send_data_completion_notice_necessity)
    ReceivedDataDecryptionKey = property(__get_received_data_decryption_key, __set_received_data_decryption_key)

    SendDataHexStr = property(__get_send_data_hex_str)
    SendDataLength = property(__get_send_data_length)
    ReceiveStatus = property(__get_receive_status)
    ReceiveAckTimeOut = property(__get_receive_ack_timeout, __set_receive_ack_timeout)
    Version = property(__get_version)
    #endregion




    #region イベントコールバック関数ラッパー
    def handler(self, func, *args):
        func(*args)

    def __ev_notify_message_event_rap(self, msg, msg_id, err_code):
        if(self.evNotifyMessageEvent is not None):
            self.handler(self.evNotifyMessageEvent, msg, msg_id, err_code)

    def __ev_notify_received_disconnect_event_rap(self, msg, status):
        if (self.evNotifyReceivedDisconnectEvent is not None):
            self.handler(self.evNotifyReceivedDisconnectEvent, msg, status)

    def __ev_notify_complete_speech_rap(self, result, time_stamp):
        if (self.evNotifyCompleteSpeech is not None):
            self.handler(self.evNotifyCompleteSpeech, result, time_stamp)

    def __ev_notify_send_speech_recognition_command_rap(self, cmd_info):
        if (self.evNotifySendSpeechRecognitionCommand is not None):
            self.handler(self.evNotifySendSpeechRecognitionCommand, cmd_info)
    #endregion

    # <summary>
    # トレース出力設定
    # </summary>
    # <returns></returns>
    def setTraceOutPut(self, val):
        self.__HzTrace.set_trace_output(val)

    # <summary>
    # 非同期メッセージ受信用リスナータスク
    # </summary>
    # <returns></returns>
    def __listenerTask(self):
        try:
            connection = None
            self.__stop_event_listener.clear()
            self.__svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__svr_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__svr_sock.bind(("0.0.0.0", self.__ReceivePort))
            self.__svr_sock.listen(8)

            #self.__HzTrace.trace_comm_message("非同期メッセージ受信スレッド開始")
            self.__HzTrace.trace_comm_message("Start, receiving thread for asynchronous messages.")
            while True:
                connection = None
                connection, address = self.__svr_sock.accept()
                rcvLen = 0
                rcvBuf = None
                if(self.__stop_event_listener.is_set()):
                    self.__ReceiveStatus = self.__DISCONNECT_REASON_CANCEL
                    #raise Exception("キャンセルリクエストが発生しました。接続元から切断します。\r\n受信データサイズ[{}]".format(rcvLen))
                    raise Exception("Occued cancel request. disconnect from connection source.\r\nreceived data size[{}]".format(rcvLen))

                #reqStartComm = msg_req_start_comm.MsgReqStartComm()
                #ackSendSpeechData = msg_ack_send_speech_data.MsgAckSendSpeechData()
                #ackStartComm = msg_ack_start_comm.MsgAckStartComm()
                notifyEndComm = msg_notify_end_comm.MsgNotifyEndComm()
                #notifyControlCommand = MsgNotifyControlCommand.new
                notifyStopComm = msg_notify_stop_comm.MsgNotifyStopComm()
                notifyCompleteReading = msg_notify_complete_speech.MsgNotifyCompleteSpeech()
                sendSpeechRecognitionCommand = msg_send_speech_recognition_command.MsgSendSpeechRecognitionCommand()
                acksendSpeechRecognitionCommand = msg_ack_send_speech_recognition_command.MsgAckSendSpeechRecognitionCommand()
                rcvEndFlg = False
                self.__ReceiveStatus = notifyStopComm.REASON_CODE_NONE    #切断発生時ステータス

                try:
                    #サーバーからの送信メッセージをチェック
                    #while True:
                    rcvEndFlg = False
                    rcvLen = 0
                    if(rcvBuf is not None):
                        rcvBuf = None

                    try:
                        if(self.__svr_sock is not None):
                            #rcvLen = await _cltStream.ReadAsync(rcvBuf, 0, rcvBuf.Length)
                            rcvBuf = connection.recv(haruzira_message.SEND_READ_DATA_MAX_SIZE)
                            #rcvBuf = rcvBuf.delete("[] ").split(',').map(&:to_i)
                            rcvLen = len(rcvBuf)
                            #rcvBuf = struct.unpack("{}B".format(rcvLen), rcvBuf)
                            #p rcvBuf

                            #print("【CL】接続元からデータを受信しました。: Data Size[#{rcvLen}]")
                            #self.__HzTrace.trace_comm_message("【CL】接続元からデータを受信しました。: Data Size[{d}]".format(rcvLen))
                            self.__HzTrace.trace_comm_message("[CL]Received a data from the connection source.: Data Size[{}]".format(rcvLen))
                            if (rcvLen <= 0):
                                #print("受信データを取得できないため、接続元から切断します。\r\n受信データサイズ[{d}]".format(rcvLen))
                                print("Disconnect from the connection source, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))
                                self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                                #raise Exception("受信データを取得できないため、接続元から切断します。\r\n受信データサイズ[{d}]".format(rcvLen))
                                raise Exception("Disconnect from the connection source, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))

                            if(self.__stop_event_listener.is_set()):
                            #elsif (@ctsClient.IsCancellationRequested)
                                self.__ReceiveStatus = self.__DISCONNECT_REASON_CANCEL
                                #raise Exception("キャンセルリクエストが発生しました。接続元から切断します。")
                                raise Exception("Occued cancel request. disconnect from connection source.")

                        else:
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_CLIENT_IREGULAR
                            raise Exception("Disconnect from the connection source, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))
                            #raise Exception("受信データを取得できないため、接続元から切断します。\r\n受信データサイズ[{d}]".format(rcvLen))

                    except Exception as ex:
                        #print("【CL listener】接続元からのデータ受信エラー：{}".format(ex.args))
                        print("[CL listener]receiving data error.：{}".format(ex.args))
                        raise Exception(ex.args)

                    #受信データ解析
                    if (rcvLen > 0):
                        if(rcvBuf[0] == haruzira_message.MSG_NOTIFY_COMPLETE_SPEECH):
                            if (rcvLen != notifyCompleteReading.total_len):
                                #受信データサイズが不正
                                self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                                #raise Exception("不正なデータを受信したため、接続元から切断します。\r\nnメッセージID[0x{0:02x}], 受信サイズ[{1:d}]".format(notifyCompleteReading.id, rcvLen))
                                raise Exception("Disconnect from the connection source, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(notifyCompleteReading.id, rcvLen))
                            notifyCompleteReading.result = rcvBuf[notifyCompleteReading.INDEX_RESULT]
                            notifyCompleteReading.time_stamp = rcvBuf[notifyCompleteReading.INDEX_TIME_STAMP:(notifyCompleteReading.INDEX_TIME_STAMP + 8)]
                            #self.__HzTrace.trace_comm_message("【CL】読み上げ完了通知受信(0x{0:02x})：Result[0x{1:02x}], TimeStamp[{2:s}]".format(notifyCompleteReading.id, notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8")))
                            self.__HzTrace.trace_comm_message("[CL]Received, Speech Completion Notice(0x{0:02x})：Result[0x{1:02x}], TimeStamp[{2:s}]".format(notifyCompleteReading.id, notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8")))
                            #コールバック関数呼び出し
                            self.__ev_notify_complete_speech_rap(notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8"))
                        elif(rcvBuf[0] == haruzira_message.MSG_NOTIFY_STOP_COMM):
                            if(rcvLen != notifyStopComm.total_len):
                                #受信データサイズが不正
                                self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                                #raise Exception("不正なデータを受信したため、接続元から切断します。\r\nメッセージID[0x{0:02x}], 受信サイズ[{1:d}]".format(notifyStopComm.id, rcvLen))
                                raise Exception("Disconnect from the connection source, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(notifyStopComm.id, rcvLen))
                            notifyStopComm.stop_code = rcvBuf[notifyStopComm.INDEX_STOP_CODE]
                            self.__ReceiveStatus = notifyStopComm.reason_code
                            #self.__HzTrace.trace_comm_message("【CL】通信停止通知受信(0x{0:02x})：Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code))
                            #self.__ev_notify_received_disconnect_event_rap(("クライアント： " + "接続元から通信停止通知を受信しました。接続元から切断します。\r\nメッセージID[0x{0:02x}], 停止コード[0x{1:02x}], 理由コード[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code)), self.__ReceiveStatus)
                            self.__HzTrace.trace_comm_message("[CL]Received, Communication Stop Notice(0x{0:02x})：Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code))
                            self.__ev_notify_received_disconnect_event_rap(("Client： " + "Received, Communication Stop Notice. disconnect from the connection source.\r\nMessage ID[0x{0:02x}], Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code)), self.__ReceiveStatus)
                            rcvEndFlg = True
                        elif(rcvBuf[0] == haruzira_message.MSG_SEND_SPEECH_RECOGNITION_COMMAND):
                            cmdCallBack = False
                            sendSpeechRecognitionCommand.size = struct.unpack(">L", rcvBuf[sendSpeechRecognitionCommand.INDEX_SIZE:(sendSpeechRecognitionCommand.INDEX_SIZE + 4)])[0]

                            if (rcvLen != sendSpeechRecognitionCommand.head_len + sendSpeechRecognitionCommand.size):
                                #受信データサイズが不正
                                #_receiveStatus = DISCONNECT_REASON_SERVER_IREGULAR
                                self.__HzTrace.trace_comm_message("Received invalid data. disconnected from access point. Message ID[0x{0:02x}], Receive data size[{1:d}]".format(sendSpeechRecognitionCommand.id, rcvLen))
                                acksendSpeechRecognitionCommand.ack_code = acksendSpeechRecognitionCommand.ACK_CODE_NG
                                acksendSpeechRecognitionCommand.err_code = acksendSpeechRecognitionCommand.ERR_CODE_RCV_DATA
                                self.__ev_notify_message_event_rap("Received invalid data. disconnected from access point. Message ID[0x{0:02x}], Receive data size[{1:d}]".format(sendSpeechRecognitionCommand.id, rcvLen), sendSpeechRecognitionCommand.id, HZ_ERROR_OTHER_REASON)
                            else:
                                sendSpeechRecognitionCommand.enc_flg = rcvBuf[sendSpeechRecognitionCommand.INDEX_ENC_FLG]
                                sendSpeechRecognitionCommand.port = struct.unpack(">H", rcvBuf[sendSpeechRecognitionCommand.INDEX_PORT:(sendSpeechRecognitionCommand.INDEX_PORT + 2)])[0]
                                sendSpeechRecognitionCommand.mode = rcvBuf[sendSpeechRecognitionCommand.INDEX_MODE]
                                sendSpeechRecognitionCommand.time_stamp = rcvBuf[sendSpeechRecognitionCommand.INDEX_TIME_STAMP:(sendSpeechRecognitionCommand.INDEX_TIME_STAMP + 8)]
                                sendSpeechRecognitionCommand.data = rcvBuf[(sendSpeechRecognitionCommand.INDEX_SIZE + 4):(sendSpeechRecognitionCommand.INDEX_SIZE + 4 + sendSpeechRecognitionCommand.size)]
                                command = ""
                                if (sendSpeechRecognitionCommand.enc_flg == sendSpeechRecognitionCommand.ENC_FLG_ON):
                                    #暗号化データ復号
                                    data_tmp = self.__encryption.cipherDecryption(self.__encryption_type, sendSpeechRecognitionCommand.data, self.__ReceivedDataDecryptionKey) 
                                    command = data_tmp.decode("utf-8")
                                else:
                                    #平文の場合
                                    command = sendSpeechRecognitionCommand.data.decode("utf-8")

                                self.__HzTrace.trace_comm_message("Received 'Send Speech Recognition Command'(0x{0:02x}) : Mode[{1:d}], Port[{2:d}], Timestamp[{3:s}], Command[{4:s}], Size[{5:d}]".format(sendSpeechRecognitionCommand.id, sendSpeechRecognitionCommand.mode, sendSpeechRecognitionCommand.port, sendSpeechRecognitionCommand.time_stamp.decode("utf-8"), command, sendSpeechRecognitionCommand.size))
                                if(command == ""):
                                    #複合化エラー
                                    acksendSpeechRecognitionCommand.ack_code = acksendSpeechRecognitionCommand.ACK_CODE_NG
                                    acksendSpeechRecognitionCommand.err_code = acksendSpeechRecognitionCommand.ERR_CODE_DECODE_ENC
                                    self.__ev_notify_message_event_rap("Failed to decryption of the received data.", sendSpeechRecognitionCommand.id, HZ_ERROR_OTHER_REASON)
                                else:
                                    #平文または複合化成功
                                    cmdCallBack = True
                                    acksendSpeechRecognitionCommand.ack_code = acksendSpeechRecognitionCommand.ACK_CODE_OK
                                    acksendSpeechRecognitionCommand.err_code = acksendSpeechRecognitionCommand.ERR_CODE_NONE
                            #応答を返す
                            acksendSpeechRecognitionCommand.time_stamp = sendSpeechRecognitionCommand.time_stamp
                            data_len, data = acksendSpeechRecognitionCommand.make_send_data()
                            if(data_len > 0):
                                connection.send(np.array(data, dtype=np.uint8))
                            else:
                                raise Exception("Error occurred in data creation. It suspend a communication process.")

                            if(cmdCallBack):
                                #コールバック関数呼び出し
                                cmdInfo = hz_speech_recognition_command_info.SpeechRecognitionCommandInfo()
                                cmdInfo.mode = sendSpeechRecognitionCommand.mode
                                cmdInfo.ip_addr = address[0]
                                cmdInfo.port = sendSpeechRecognitionCommand.port
                                cmdInfo.command = command
                                cmdInfo.timestamp = sendSpeechRecognitionCommand.time_stamp.decode("utf-8")
                                self.__ev_notify_send_speech_recognition_command_rap(cmdInfo)

                        else:
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("不正なデータを受信しました。Message ID[0x{0:02x}], 受信サイズ[{1:d}]".format(rcvBuf[0], rcvLen))
                            raise Exception("Disconnect from the connection source, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(rcvBuf[0], rcvLen))

                        if(rcvEndFlg):
                            break

                except Exception as ex:
                    #self.__ev_notify_received_disconnect_event_rap("非同期メッセージ受信スレッド： {}".format(ex.args), self.__ReceiveStatus)
                    self.__ev_notify_received_disconnect_event_rap("Asynchronous message receiving thread： {}".format(ex.args), self.__ReceiveStatus)
                    #if (ex.HResult != haruzira_message.HRSEULT_SOCKET_CLOSED)
                    #    #self.__notifyEndCommProc()
                    #    self.__ev_notify_received_disconnect_event_rap("受信スレッド： " + ex, self.__ReceiveStatus)
                    #end
                finally:
                    if(connection is not None):
                        connection.close()
                        connection = None
            #loop
        except Exception as ex:
            if(self.__ReceiveStatus == 0x00):
                self.__ReceiveStatus = self.__DISCONNECT_REASON_CLIENT_IREGULAR
            self.__ackSendSpeechDataAutoResetEvent.set()
            #self.__ev_notify_received_disconnect_event_rap("非同期メッセージ受信スレッド： {}".format(ex.args), self.__ReceiveStatus)
            if(self.__svr_sock != None and self.__stop_event_listener.is_set() != True):
                self.__ev_notify_received_disconnect_event_rap("Asynchronous message receiving thread： {}".format(ex.args), self.__ReceiveStatus)
        finally:
            if(connection is not None):
                connection.close()
                connection = None

            if(self.__svr_sock is not None):
                self.__svr_sock.close()
                self.__svr_sock = None

            if(self.__listenTask is not None):
                self.__listenTask = None
        #self.__HzTrace.trace_comm_message("非同期メッセージ受信スレッド終了")
        self.__HzTrace.trace_comm_message("Completed, asynchronous message receiving thread.")



    # <summary>
    # 受信ワーカータスク
    # </summary>
    # <returns></returns>
    def __receive_worker(self):
        #Thread.abort_on_exception = True
        rcvLen = 0
        rcvBuf = None
        reqStartComm = msg_req_start_comm.MsgReqStartComm()
        ackSendSpeechData = msg_ack_send_speech_data.MsgAckSendSpeechData()
        ackStartComm = msg_ack_start_comm.MsgAckStartComm()
        notifyEndComm = msg_notify_end_comm.MsgNotifyEndComm()
        #notifyControlCommand = MsgNotifyControlCommand.new
        notifyStopComm = msg_notify_stop_comm.MsgNotifyStopComm()
        notifyCompleteReading = msg_notify_complete_speech.MsgNotifyCompleteSpeech()
        rcvEndFlg = False
        self.__ReceiveStatus = notifyStopComm.REASON_CODE_NONE    #切断発生時ステータス
        self.__stop_event_rcv.clear()

        try:
            #self.__HzTrace.trace_comm_message("受信ワーカースレッド開始")
            self.__HzTrace.trace_comm_message("Start, receiving worker thread.")
            #サーバーからの送信メッセージをチェック
            while True:
                rcvEndFlg = False
                rcvLen = 0
                self.__ReceiveStatus = 0x00
                if(rcvBuf is not None):
                    rcvBuf = None

                try:
                    if(self.__cltSocket is not None):
                        #rcvLen = await _cltStream.ReadAsync(rcvBuf, 0, rcvBuf.Length)
                        rcvBuf = self.__cltSocket.recv(haruzira_message.SEND_READ_DATA_MAX_SIZE)
                        #rcvBuf = rcvBuf.delete("[] ").split(',').map(&:to_i)
                        rcvLen = len(rcvBuf)
                        #rcvBuf = struct.unpack("{}B".format(rcvLen), rcvBuf)
                        #p rcvBuf

                        #print("【CL】接続先からデータを受信しました。: Data Size[#{rcvLen}]")
                        #self.__HzTrace.trace_comm_message("【CL】接続先からデータを受信しました。: Data Size[{}]".format(rcvLen))
                        self.__HzTrace.trace_comm_message("[CL]Received a data from the access point.: Data Size[{}]".format(rcvLen))
                        if(rcvLen <= 0):
                            break
                            #print("受信データを取得できないため、接続先から切断します。\r\n受信データサイズ[{}]".format(rcvLen))
                            print("Disconnect from the access point, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("受信データを取得できないため、接続先から切断します。\r\n受信データサイズ[{}]".format(rcvLen)
                            raise Exception("Disconnect from the access point, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))
                        if(self.__stop_event_rcv.is_set()):
                        #elsif (@ctsClient.IsCancellationRequested)
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_CANCEL
                            #raise Exception("キャンセルリクエストが発生しました。接続元から切断します。\r\n受信データサイズ[{}]".format(rcvLen))
                            raise Exception("Occued cancel request. disconnect from connection source.\r\nreceived data size[{}]".format(rcvLen))

                    else:
                        self.__ReceiveStatus = self.__DISCONNECT_REASON_CLIENT_IREGULAR
                        #raise Exception("受信データを取得できないため、接続先から切断します。\r\n受信データサイズ[#{rcvLen}]")
                        raise Exception("Disconnect from the access point, because it can't  to receive any data.\r\nData Size[{}]".format(rcvLen))

                except Exception as ex:
                    self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                    #print("【CL】接続先からのデータ受信エラー：{}".format(ex.args))
                    print("[CL listener]receiving data error.：{}".format(ex.args))
                    raise Exception(ex.args)

                #受信データ解析
                if(rcvLen > 0):
                    if(rcvBuf[0] == haruzira_message.MSG_ACK_START_COMM):
                        if(rcvLen != ackStartComm.total_len):
                            #受信データサイズが不正
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("不正なデータを受信したため、接続先から切断します。\r\nnメッセージID[0x{0:02x}], 受信サイズ[{1:d}]".format(ackStartComm.id, rcvLen))
                            raise Exception("Disconnect from the access point, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(ackStartComm.id, rcvLen))
                        ackStartComm.ack_code = rcvBuf[ackStartComm.INDEX_ACK_CODE]
                        ackStartComm.err_code = rcvBuf[ackStartComm.INDEX_ERR_CODE]
                        #self.__HzTrace.trace_comm_message("【CL】通信開始応答受信(0x{0:02x})：Ack Code[0x{1:02x}], Error Code[0x{2:02x}]".format(ackStartComm.id, ackStartComm.ack_code, ackStartComm.err_code))
                        self.__HzTrace.trace_comm_message("[CL]Received, Responce of Communication Start Request(0x{0:02x})：Ack Code[0x{1:02x}], Error Code[0x{2:02x}]".format(ackStartComm.id, ackStartComm.ack_code, ackStartComm.err_code))
                        if(ackStartComm.ack_code == ackStartComm.ACK_CODE_NG):
                            #エラー発生時
                            self.__ReceiveStatus = ackStartComm.err_code
                            #self.__ev_notify_message_event_rap("接続先からエラーコードを受信しました。\r\nメッセージID[0x{0:02x}], エラーコード[0x{1:02x}]".format(ackStartComm.id, ackStartComm.err_code), ackStartComm.id, ackStartComm.err_code)
                            self.__ev_notify_message_event_rap("Received error code from the access point.\r\nMessage ID[0x{0:02x}], Error Code[0x{1:02x}]".format(ackStartComm.id, ackStartComm.err_code), ackStartComm.id, ackStartComm.err_code)
                            rcvEndFlg = True
                        self.__ackStartCommAutoResetEvent.set()
                    elif(rcvBuf[0] == haruzira_message.MSG_ACK_SEND_SPEECH_DATA):
                        if(rcvLen != ackSendSpeechData.total_len):
                            #受信データサイズが不正
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("不正なデータを受信したため、接続先から切断します。\r\nメッセージID[0x{0:02x}], 受信サイズ[{1:d}]".format(ackSendSpeechData.id, rcvLen))
                            raise Exception("Disconnect from the access point, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(ackSendSpeechData.id, rcvLen))
                        ackSendSpeechData.ack_code = rcvBuf[ackSendSpeechData.INDEX_ACK_CODE]
                        ackSendSpeechData.err_code = rcvBuf[ackSendSpeechData.INDEX_ERR_CODE]
                        #self.__HzTrace.trace_comm_message("【CL】読み上げデータ送信応答受信(0x{0:02x})：Ack Code[0x{1:02x}], Error Code[0x{2:02x}]".format(ackSendSpeechData.id, ackSendSpeechData.ack_code, ackSendSpeechData.err_code))
                        self.__HzTrace.trace_comm_message("[CL]Received, Responce of Send Speech Data(0x{0:02x})：Ack Code[0x{1:02x}], Error Code[0x{2:02x}]".format(ackSendSpeechData.id, ackSendSpeechData.ack_code, ackSendSpeechData.err_code))
                        if(ackSendSpeechData.ack_code == ackSendSpeechData.ACK_CODE_NG) :
                            #エラー発生時
                            self.__ReceiveStatus = ackSendSpeechData.err_code
                            #self.__ev_notify_message_event_rap("接続先からエラーコードを受信しました。\r\nメッセージID[0x{0:02x}], エラーコード[0x{1:02x}]".format(ackSendSpeechData.id, ackSendSpeechData.err_code), ackSendSpeechData.id, ackSendSpeechData.err_code)
                            self.__ev_notify_message_event_rap("Received error code from the access point.\r\nMessage ID[0x{0:02x}], Error Code[0x{1:02x}]".format(ackSendSpeechData.id, ackSendSpeechData.err_code), ackSendSpeechData.id, ackSendSpeechData.err_code)
                            rcvEndFlg = True
                        self.__ackSendSpeechDataAutoResetEvent.set()
                    elif(rcvBuf[0] == haruzira_message.MSG_NOTIFY_COMPLETE_SPEECH):
                        if(rcvLen != notifyCompleteReading.total_len):
                            #受信データサイズが不正
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("不正なデータを受信したため、接続先から切断します。\r\nnメッセージID[0x{0:02x}], 受信サイズ[{1:d}]".format(notifyCompleteReading.id, rcvLen))
                            raise Exception("Disconnect from the access point, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(notifyCompleteReading.id, rcvLen))
                        notifyCompleteReading.result = rcvBuf[notifyCompleteReading.INDEX_RESULT]
                        notifyCompleteReading.time_stamp = rcvBuf[notifyCompleteReading.INDEX_TIME_STAMP:(notifyCompleteReading.INDEX_TIME_STAMP + 8)]
                        #self.__HzTrace.trace_comm_message("【CL】読み上げ完了通知受信(0x{0:02x})：Result[0x{1:02x}], TimeStamp[{2:s}]".format(notifyCompleteReading.id, notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8")))
                        self.__HzTrace.trace_comm_message("[CL]Received, Speech Completion Notice(0x{0:02x})：Result[0x{1:02x}], TimeStamp[{2:s}]".format(notifyCompleteReading.id, notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8")))
                        #コールバック関数呼び出し
                        self.__ev_notify_complete_speech_rap(notifyCompleteReading.result, notifyCompleteReading.time_stamp.decode("utf-8"))
                    elif(rcvBuf[0] == haruzira_message.MSG_NOTIFY_STOP_COMM):
                        if(rcvLen != notifyStopComm.total_len):
                            #受信データサイズが不正
                            self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                            #raise Exception("不正なデータを受信したため、接続先から切断します。\r\nメッセージID[{0:{0:02x}}], 受信サイズ[{1:d}]", notifyStopComm.id, rcvLen)
                            raise Exception("Disconnect from the access point, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(notifyStopComm.id, rcvLen))
                        notifyStopComm.stop_code = rcvBuf[notifyStopComm.INDEX_STOP_CODE]
                        self.__ReceiveStatus = notifyStopComm.reason_code
                        #self.__HzTrace.trace_comm_message("【CL】通信停止通知受信(0x{0:02x})：Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code))
                        #self.__ev_notify_received_disconnect_event_rap(("クライアント： " + "接続先から通信停止通知を受信しました。接続先から切断します。\r\nメッセージID[0x%02x], 停止コード[0x%02x], 理由コード[0x%02x]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code)), @ReceiveStatus)
                        self.__HzTrace.trace_comm_message("[CL]Received, Communication Stop Notice(0x{0:02x})：Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code))
                        self.__ev_notify_received_disconnect_event_rap(("Client： " + "Received, Communication Stop Notice. disconnect from the access point.\r\nMessage ID[0x{0:02x}], Stop Code[0x{1:02x}], Reason Code[0x{2:02x}]".format(notifyStopComm.id, notifyStopComm.stop_code, notifyStopComm.reason_code)), self.__ReceiveStatus)
                        rcvEndFlg = True
                    else:
                        self.__ReceiveStatus = self.__DISCONNECT_REASON_SERVER_IREGULAR
                        #raise Exception("不正なデータを受信しました。Message ID[0x{0:02x}], 受信サイズ[{1:d}]".format(rcvBuf[0], rcvLen))
                        raise Exception("Disconnect from the access point, because it has received invaild data.\r\nMessage ID[0x{0:02x}], Data Size[{1:d}]".format(rcvBuf[0], rcvLen))

                    if(rcvEndFlg):
                        break



        except Exception as ex:
            #self.__ev_notify_received_disconnect_event_rap("受信スレッド： {}".format(ex.args), self.__ReceiveStatus)
            self.__ev_notify_received_disconnect_event_rap("Receiving worker thread： {}".format(ex.args), self.__ReceiveStatus)
            #if (ex.HResult != HaruZiraMessage.HRSEULT_SOCKET_CLOSED)
            #    #self.__notifyEndCommProc()
            #    self.__ev_notify_received_disconnect_event_rap("受信スレッド： " + ex.Message, @ReceiveStatus)
        finally:
            if(self.__cltSocket != None):
                self.__cltSocket.close()
                self.__cltSocket = None
            #同期オブジェクトの解除
            self.__ackStartCommAutoResetEvent.set()
            self.__ackSendSpeechDataAutoResetEvent.set()
            #self.__HzTrace.trace_comm_message("受信ワーカースレッド終了")
            self.__HzTrace.trace_comm_message("Completed receiving worker thread.")


    # <summary>
    # 通信開始応答受信待機スレッド
    # </summary>
    #def __wait_worker_ack_start_com(self):
    #    self.__ackStartCommAutoResetEvent.wait()

    # <summary>
    # 読み上げデータ送信応答受信待機スレッド
    # </summary>
    #def __wait_worker_ack_send_speech_data(self):
    #    self.__ackSendSpeechDataAutoResetEvent.wait()

    # <summary>
    # 通信開始要求(0x00)
    # </summary>
    # <param name="name">アカウント名</param>
    # <param name="passwd">パスワード</param>
    # <param name="strEnc">暗号化キー</param>
    # <returns>True:OK, False:NG</returns>
    def __reqStartCommProc(self, name = "", passwd = "", strEncKey = ""):
        data = None
        ret_len = 0 
        self.__ReceiveStatus = 0 
        reqStartComm = msg_req_start_comm.MsgReqStartComm() 
        ackStartComm = msg_ack_start_comm.MsgAckStartComm() 
        ret = False 

        try:
            #接続状態の確認
            if (self.__cltSocket is not None):
                self.__cltSocket.close() 
                self.__cltSocket = None 
                try:
                    if(self.__work_rcv is not None):
                        self.__work_rsv.join(haruzira_message.THREAD_JOIN_TIME_OUT)
                except Exception as ex:
                    print(ex.args)
                    #スレッド終了待ちのタイムアウトが発生しました。スレッドを強制終了しました。
                    self.__stop_event_rcv.set()

            #接続
            self.__cltSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__cltSocket.connect((self.__ServerIP, self.__ServerPortNo))
            #print "接続OK"

            self.__ackStartCommAutoResetEvent = threading.Event() 
            self.__ackSendSpeechDataAutoResetEvent = threading.Event() 

            #受信ワーカータスク起動
            self.__work_rcv = threading.Thread(target=self.__receive_worker)
            self.__work_rcv.start() 
            time.sleep(0.5)

            #通信開始要求(0x00)
            if(name.strip() != "" and passwd.strip() != ""):
                reqStartComm.cer_flg = reqStartComm.CER_FLG_ON 
            else:
                reqStartComm.cer_flg = reqStartComm.CER_FLG_OFF 

            if (strEncKey.strip() != "" and reqStartComm.cer_flg == reqStartComm.CER_FLG_ON):
                #暗号化
                reqStartComm.enc_flg = reqStartComm.ENC_FLG_ON 
                reqStartComm.passwd = self.__encryption.cipherEncryption(passwd.encode("utf-8"), self.__encryption_type, strEncKey)
                #p reqStartComm.passwd
                #Debug
                #decPasswd = self.__encryption.cipherDecryption(self.__encryption_type, reqStartComm.passwd.decode("utf-8"), strEncKey) 
                #self.__HzTrace.trace_comm_message("複合後パスワード：{}".format(decPasswd)) 
            else:
                reqStartComm.enc_flg = reqStartComm.ENC_FLG_OFF 
                reqStartComm.passwd = list(passwd.strip().encode("utf-8"))

            reqStartComm.port = self.__ReceivePort
            if(name != "" and passwd != ""):
                reqStartComm.name = list(name.strip().encode("utf-8")) 
                reqStartComm.name_len = len(reqStartComm.name)
                reqStartComm.passwd_len = len(reqStartComm.passwd)
                #print "account[#{reqStartComm.name.encode("utf-8")}] len:#{reqStartComm.name_len}, passwd len: #{reqStartComm.passwd_len}"
            reqStartComm.sdk_lang_type = self.__SDK_LANG_TYPE
            reqStartComm.sdk_versions = self.__SdkVersions
            ret_len, data = reqStartComm.make_send_data()
            #p ret_len, data
            if(ret_len > 0):
                self.__ackStartCommAutoResetEvent.clear()
                self.__cltSocket.send(np.array(data, dtype=np.uint8))
            else:
                #raise Exception("送信データの生成エラー。\r\n通信処理を停止します。")
                raise Exception("Creation error of sending data. and then the communicationn stop.")

            #self.__HzTrace.trace_comm_message("【CL】通信開始要求送信(0x{0:02x})：Cer[{1:d}] Enc[{2:d}], Port[{3:d}], Name[{4:s}], Passwd[{5:s}], Name Len[{6:d}], Passwd Len[{7:d}]".format(
            self.__HzTrace.trace_comm_message("[CL]Send, Communication Start Request(0x{0:02x})：Cer[{1:d}] Enc[{2:d}], Port[{3:d}], Name[{4:s}], Passwd[{5:s}], Name Len[{6:d}], Passwd Len[{7:d}], Lang Type[{8:d}], Version[{9:d}].[{10:d}]".format(
                reqStartComm.id, reqStartComm.cer_flg, reqStartComm.enc_flg, reqStartComm.port, name if reqStartComm.name is not None else "", 
                passwd if reqStartComm.passwd is not None else "", reqStartComm.name_len, reqStartComm.passwd_len, reqStartComm.sdk_lang_type, reqStartComm.sdk_versions[0], reqStartComm.sdk_versions[1]))

            #通信開始応答受信(0x10)
            if(self.__ackStartCommAutoResetEvent.wait(self.__ReceiveAckTimeOut) != True):
                #self.__ackStartCommAutoResetEvent.set()
                #応答待ちのタイムアウトが発生しました。通信処理を中断しました。
                #print("【CL】通信開始応答受信(0x%02x)：待機結果[%s]" % [reqStartComm.id, "Time Out"]) 
                #self.__ev_notify_message_event_rap("応答待ちのタイムアウトが発生しました。通信処理を中断します。", reqStartComm.id, HZ_ERROR_RECEIVE_TIMEOUT)
                print("[CL]Received, Responce of Communication Start Request(0x{0:02x})：Waiting Result[{1:s}]".format(ackStartComm.id, "Time Out")) 
                self.__ev_notify_message_event_rap("Timeout has occurred by waiting for the response. and then the communication stop.", ackStartComm.id, haruzira_message.HZ_ERROR_RECEIVE_TIMEOUT)
                return False
            else:
                if(self.__ReceiveStatus != 0x00):
                    #raise Exception("通信中にエラーが発生しました。\r\n通信処理を中断します。")
                    raise Exception("A error occurred on the communication. and then the communication stop.")
                else:
                    #self.__HzTrace.trace_comm_message("【CL】通信開始応答受信(0x{0:02x})：待機結果[{1:s}]".format(reqStartComm.id, "OK"))
                    self.__HzTrace.trace_comm_message("【CL】[CL]Received, Responce of Communication Start Request(0x{0:02x})：Waiting Result[{1:s}]".format(ackStartComm.id, "OK"))
            #self.__ackStartCommAutoResetEvent.clear()

            ret = True
        except Exception as ex:
            self.__ev_notify_message_event_rap(str(ex.args), reqStartComm.id, haruzira_message.HZ_ERROR_OTHER_REASON)
            print("Client： {}".format(ex.args)) 
            if(self.__cltSocket != None):
                #if (@work_rcv.alive)
                    self.__cltSocket.close() 
                    self.__cltSocket = None 
                    self.__ackStartCommAutoResetEvent.set()
                #end
            ret = False 
        finally:
            return ret

    # <summary>
    # 通信終了通知(0x01)
    # </summary>
    # <param name="err_code">パスワード</param>
    # <returns>True:OK, False:NG</returns>
    def __notifyEndCommProc(self, err_code):
        notifyEndComm = msg_notify_end_comm.MsgNotifyEndComm()
        data = None
        ret_len = 0
        self.__ReceiveStatus = 0
        ret = False 

        try:
            #接続状態の確認
            if(self.__cltSocket is None):
                return True

            #通信終了通知(0x01)
            if(err_code == notifyEndComm.ERR_CODE_NONE):
                #正常
                notifyEndComm.end_code = notifyEndComm.END_CODE_OK
                notifyEndComm.err_code = notifyEndComm.ERR_CODE_NONE
            else:
                #エラー有
                notifyEndComm.end_code = notifyEndComm.END_CODE_NG
                notifyEndComm.err_code = err_code

            ret_len, data = notifyEndComm.make_send_data()
            #p len, data
            if(ret_len > 0):
                self.__cltSocket.send(np.array(data, dtype=np.uint8))
            else:
                #raise Exception("送信データの生成エラー。\r\n通信処理を停止します。")
                raise Exception("Creation error of sending data. and then the communicationn stop.")

            #self.__HzTrace.trace_comm_message("【CL】通信終了通知送信(0x{0:02x})：End Code[0x{1:02x}], Error Code[0x{2:02x}]".format(notifyEndComm.id, notifyEndComm.end_code, notifyEndComm.err_code))
            self.__HzTrace.trace_comm_message("[CL]Send, Communication End Notice(0x{0:02x})：End Code[0x{1:02x}], Error Code[0x{2:02x}]".format(notifyEndComm.id, notifyEndComm.end_code, notifyEndComm.err_code))

            #サーバーが受信することを考慮
            time.sleep(3) 
            
            self.__work_rcv.join(haruzira_message.THREAD_JOIN_TIME_OUT)
            if(self.__work_rcv is not None and self.__work_rcv.is_alive):
                #スレッド終了待ちのタイムアウトが発生しました。スレッドを強制終了しました。
                self.__stop_event_rcv.set()

            if(self.__cltSocket is not None):
                self.__cltSocket.close()

            ret = True
        except Exception as ex:
            self.__ev_notify_message_event_rap(str(ex.args), notifyEndComm.id, haruzira_message.HZ_ERROR_OTHER_REASON)

            #if (ex.HResult != haruzira_message.HRSEULT_SOCKET_CLOSED)
            #    self.__ev_notify_message_event_rap("クライアント： " + str(ex.args))
            #end

            ret = False
        finally:
            return ret

    # <summary>
    # 読み上げデータ送信（手動）
    # </summary>
    # <returns>OK:タイムスタンプ文字列(00:00:00形式), NG:None</returns>
    def __sendSpeechData(self):
        data = None
        ret_len = 0
        self.__ReceiveStatus = 0
        sendSpeechData = msg_send_speech_data.MsgSendSpeechData()
        ackSendSpeechData = msg_ack_send_speech_data.MsgAckSendSpeechData()
        t = datetime.datetime.today()
        timeStamp = "{0:02d}:{1:02d}:{2:02d}".format(t.hour, t.minute, t.second)

        try:
            if(self.__cltSocket is None):
                #raise Exception("未接続です。\r\n送信先へ接続して下さい。")
                raise Exception("No connection. You must connect to the access point.")


            #読み上げデータ送信(0x03)
            if(self.__ReqSendDataAccountName != "" and self.__ReqSendDataEncryptKey != ""):
                #暗号化
                sendSpeechData.enc_flg = sendSpeechData.ENC_FLG_ON
                sendSpeechData.data = self.__encryption.cipherEncryption(self.__ReqSendDataText.encode("UTF-8"), self.__encryption_type, self.__ReqSendDataEncryptKey)
            else:
                #平文
                sendSpeechData.enc_flg = sendSpeechData.ENC_FLG_OFF
                sendSpeechData.data = self.__ReqSendDataText.encode("UTF-8")
            #p sendSpeechData.data

            if(self.__ReqSendDataAccountName != ""):
                sendSpeechData.name = self.__ReqSendDataAccountName.encode("UTF-8")
                sendSpeechData.name_len = len(sendSpeechData.name)
            sendSpeechData.data_type = self.__ReqSendDataSpeechMode
            sendSpeechData.priority = self.__ReqSendDataSpeechLevel
            sendSpeechData.lang_code = self.__ReqSendDataSpeechLocaleId
            sendSpeechData.gender = self.__ReqSendDataSpeechGender
            sendSpeechData.age = self.__ReqSendDataSpeechAge
            sendSpeechData.repeat = self.__ReqSendDataSpeechRepeat
            sendSpeechData.time_stamp = timeStamp.encode("UTF-8")
            sendSpeechData.completion_notice_necessity = self.__ReqSendDataCompletionNoticeNecessity
            sendSpeechData.size = len(sendSpeechData.data)
            self.__SendDataLength = sendSpeechData.size         #Debug用

            ret_len, data = sendSpeechData.make_send_data()
            #p ret_len, data
            #p ret_len
            if(ret_len > 0):
                self.__ackSendSpeechDataAutoResetEvent.clear()
                self.__cltSocket.send(np.array(data, dtype=np.uint8))
            else:
                #raise Exception("送信データの生成エラー。\r\n通信処理を停止します。")
                raise Exception("Creation error of sending data. and then the communicationn stop.")

            #self.__HzTrace.trace_comm_message("【CL】読み上げデータ送信(0x{0:02x})：Enc[{1:d}], Size[{2:d}]".format(sendSpeechData.id, sendSpeechData.enc_flg, sendSpeechData.size))
            self.__HzTrace.trace_comm_message("[CL]Send, Send Speech Data(0x{0:02x})：Enc[{1:d}], Size[{2:d}], CompleteMsg[{3:d}]".format(sendSpeechData.id, sendSpeechData.enc_flg, sendSpeechData.size, sendSpeechData.completion_notice_necessity))


            #読み上げデータ送信応答待機(0x12)
            if(self.__ackSendSpeechDataAutoResetEvent.wait(self.__ReceiveAckTimeOut) != True):
                #self.__ackSendSpeechDataAutoResetEvent.set()
                #応答待ちのタイムアウトが発生しました。通信処理を中断しました。
                timeStamp = None
                #print("【CL】読み上げデータ送信応答受信(0x{0:02x})：待機結果[{1:s}]".format(sendSpeechData.id, "Time Out"))
                #self.__ev_notify_message_event_rap("応答待ちのタイムアウトが発生しました。通信処理を中断します。", sendSpeechData.id, HZ_ERROR_RECEIVE_TIMEOUT)
                print("[CL]Received, Responce of Send Speech Data(0x{0:02x})：Waiting Result[{1:s}]".format(ackSendSpeechData.id, "Time Out")) 
                self.__ev_notify_message_event_rap("Timeout has occurred by waiting for the response. and then the communication stop.", ackSendSpeechData.id, haruzira_message.HZ_ERROR_RECEIVE_TIMEOUT)
            else:
                if(self.__ReceiveStatus != 0x00):
                    timeStamp = None
                    return None
                else:
                    #self.__HzTrace.trace_comm_message("【CL】読み上げデータ送信応答受信(0x{0:02x})：待機結果[{1:s}]".format(sendSpeechData.id, "OK"))
                    self.__HzTrace.trace_comm_message("[CL]Received, Responce of Send Speech Data(0x{0:02x})：Waiting Result[{1:s}]".format(ackSendSpeechData.id, "OK"))
                #self.__ackSendSpeechDataAutoResetEvent.clear()

        except Exception as ex:
            self.__ev_notify_message_event_rap(str(ex.args), sendSpeechData.id, haruzira_message.HZ_ERROR_OTHER_REASON)
            print(ex.args)
            timeStamp = None
        finally:
            return timeStamp

    # <summary>
    # 読み上げデータ送信（自動）
    # </summary>
    # <returns>OK:タイムスタンプ文字列(00:00:00形式), NG:None</returns>
    def sendSpeechDataEx(self):
        timeStamp = ""
        notifyEndComm = msg_notify_end_comm.MsgNotifyEndComm()

        try:

            #電文シーケンス開始
            #通信開始要求(0x00)
            if (self.__ReqSendDataAccountName is not None and self.__ReqSendDataPasswd is not None and self.__ReqSendDataEncryptKey is not None):
                #暗号化パスワード認証
                retStatus = self.__reqStartCommProc(self.__ReqSendDataAccountName, self.__ReqSendDataPasswd, self.__ReqSendDataEncryptKey)
            elif(self.__ReqSendDataAccountName is not None and self.__ReqSendDataPasswd is not None):
                #パスワード認証
                retStatus = self.__reqStartCommProc(self.__ReqSendDataAccountName, self.__ReqSendDataPasswd)
            else:
                #認証無
                retStatus = self.__reqStartCommProc()
            if (retStatus != True):
                #print("【CL】通信開始応答受信(0x{0:02x})：待機結果[{1:s}]".format(reqStartComm.id, "Time Out")) 
                #raise Exception("通信開始要求メッセージ送信に失敗しました。\r\n通信処理を中断します。")
                print("[CL]Received, Responce of Communication Start Request(0x{0:02x})：Waiting Result[{1:s}]".format(reqStartComm.id, "Time Out")) 
                raise Exception("Sending the message of Communication Strat Request has failed. and then the communication stop.")

            #非同期メッセージ受信タスク起動
            self.startAsynchronousListener()

            #読み上げデータ送信(0x03)
            if(self.__ReqSendDataAccountName is not None and self.__ReqSendDataEncryptKey is not None):
                #暗号化(アカウント名および暗号化キー有)
                self.__ReqSendDataEncrypt = True
            elif(self.__ReqSendDataAccountName is None and self.__ReqSendDataEncryptKey is not None):
                #暗号化（暗号化キーのみ）エラーケース
                self.__ReqSendDataAccountName = ""
                self.__ReqSendDataEncrypt = True
            elif(self.__ReqSendDataAccountName is not None and self.__ReqSendDataEncryptKey is None):
                #平文（アカウント名のみ）
                self.__ReqSendDataEncrypt = False
                self.__ReqSendDataEncryptKey = ""
            else:
                #平文(認証が有効の場合はエラーとなる)
                self.__ReqSendDataAccountName = ""
                self.__ReqSendDataEncrypt = False
                self.__ReqSendDataEncryptKey = ""
            timeStamp = self.__sendSpeechData()


            #通信終了通知(0x01)
            if(timeStamp is None or self.__ReceiveStatus != 0x00):
                self.__notifyEndCommProc(notifyEndComm.ERR_CODE_OTHER_REASONS)
            else:
                self.__notifyEndCommProc(notifyEndComm.ERR_CODE_NONE)

        except Exception as ex:
            self.__HzTrace.trace_comm_message("{}".format(ex.args)) 
            timeStamp = None
        finally:
            return timeStamp


    # <summary>
    # 非同期メッセージ受信タスク起動
    # </summary>
    # <returns></returns>
    def startAsynchronousListener(self):
        try:
            #非同期メッセージ受信タスク起動
            if(self.__listenTask is None):
                self.__listenTask = threading.Thread(target=self.__listenerTask)
                self.__listenTask.start()

        except Exception as ex:
            self.__HzTrace.trace_comm_message("{}".format(ex.args)) 


    # <summary>
    # 非同期メッセージ受信スレッドの終了
    # </summary>
    def cancelAsynchronousListener(self):
        if (self.__listenTask is not None):
            self.__stop_event_listener.set()
            #接続
            lsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lsoc.connect(("127.0.0.1", self.__ReceivePort))
            if (self.__listenTask is not None):
                self.__listenTask.join(3)
            lsoc.close()
            self.__listenTask = None
            #self.__HzTrace.trace_comm_message("非同期メッセージ受信スレッドをキャンセルしました。")
            self.__HzTrace.trace_comm_message("The thread for receiving some asynchronous messsages was canceled.")

    # <summary>
    # 読み上げデータ送信の停止（中断）
    # </summary>
    def stopSendSpeechData(self):
        if (self.__work_rcv is not None):
            self.__stop_event_rcv.set()
            self.__work_rcv = None
            #self.__HzTrace.trace_comm_message("読み上げデータ送信処理をキャンセルしました。")
            self.__HzTrace.trace_comm_message("The sending proccess for send of Speech Data was canceled.")


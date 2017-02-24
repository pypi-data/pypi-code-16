# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message

# <summary>
# 読み上げデータ送信応答メッセージ(0x11)
# </summary>
class MsgAckSendSpeechData(object):

    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_ACK_CODE = 1        #応答コード
    __INDEX_ERR_CODE = 2        #エラーコード(異常時)
    __INDEX_PADDING = 3         #アライメント


    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #応答コード
    __ACK_CODE_OK = 0x00      #正常
    __ACK_CODE_NG = 0x01      #異常
    #エラーコード(異常時)
    __ERR_CODE_NONE = 0x00                 #エラーなし
    __ERR_CODE_RCV_DATA = 0x01             #受信データエラー
    __ERR_CODE_CREATE_ACK_DATA = 0x02      #応答データ生成エラー
    __ERR_CODE_DECODE_ENC = 0x03           #暗号化データ復号エラー
    __ERR_CODE_UNKNOWN_IP = 0x04           #IPアドレスが不正
    __ERR_CODE_ENCRIPTION_DISABLE = 0x05   #暗号化無効（パスワード認証が無効）
    __ERR_CODE_BUFFER_FULL = 0x06          #バッファーフル
    __ERR_CODE_OTHER_REASONS = 0x10        #その他原因によるエラー
    #endregion

    def __init__(self):

        self.__id = haruzira_message.MSG_ACK_SEND_SPEECH_DATA          #メッセージID
        self.__ack_code = 0x00                      #応答コード
        self.__err_code = 0x00                      #エラーコード(異常時)
        self.__padding = 5*[0x00]         #アライメント
        self.__total_len = 8                        #送信フィールド合計サイズ


    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_ack_code(self):
        return self.__INDEX_ACK_CODE

    def __get_index_err_code(self):
        return self.__INDEX_ERR_CODE

    def __get_index_padding(self):
        return self.__INDEX_PADDING
    #endregion


    #region アクセサ定義(送信メンバデータ値)
    def __get_ack_code_ok(self):
        return self.__ACK_CODE_OK

    def __get_ack_code_ng(self):
        return self.__ACK_CODE_NG

    def __get_err_code_none(self):
        return self.__ERR_CODE_NONE

    def __get_err_code_rcv_data(self):
        return self.__ERR_CODE_RCV_DATA

    def __get_err_code_create_ack_data(self):
        return self.__ERR_CODE_CREATE_ACK_DATA

    def __get_err_code_decode_enc(self):
        return self.__ERR_CODE_DECODE_ENC

    def __get_err_code_unknown_ip(self):
        return self.__ERR_CODE_UNKNOWN_IP

    def __get_err_code_encription_disable(self):
        return self.__ERR_CODE_ENCRIPTION_DISABLE

    def __get_err_code_buffer_full(self):
        return self.__ERR_CODE_BUFFER_FULL

    def __get_err_code_other_reasons(self):
        return self.__ERR_CODE_OTHER_REASONS
    #endregion

    #region アクセサ定義
    def __get_ack_code(self):
        return self.__ack_code

    def __set_ack_code(self, ack_code):
        self.__ack_code = ack_code

    def __get_err_code(self):
        return self.__err_code

    def __set_err_code(self, err_code):
        self.__err_code = err_code

    def __get_padding(self):
        return self.__padding

    def __set_padding(self, padding):
        self.__padding = padding

    def __get_id(self):
        return self.__id

    def __get_total_len(self):
        return self.__total_len
    #endregion



    #region Property
    INDEX_ID = property(__get_index_id)
    INDEX_ACK_CODE = property(__get_index_ack_code)
    INDEX_ERR_CODE = property(__get_index_err_code)
    INDEX_PADDING = property(__get_index_padding)

    ACK_CODE_OK = property(__get_ack_code_ok)
    ACK_CODE_NG = property(__get_ack_code_ng)
    ERR_CODE_NONE = property(__get_err_code_none)
    ERR_CODE_RCV_DATA = property(__get_err_code_rcv_data)
    ERR_CODE_CREATE_ACK_DATA = property(__get_err_code_create_ack_data)
    ERR_CODE_DECODE_ENC = property(__get_err_code_decode_enc)
    ERR_CODE_UNKNOWN_IP = property(__get_err_code_unknown_ip)
    ERR_CODE_ENCRIPTION_DISABLE = property(__get_err_code_encription_disable)
    ERR_CODE_BUFFER_FULL = property(__get_err_code_buffer_full)
    ERR_CODE_OTHER_REASONS = property(__get_err_code_other_reasons)

    ack_code = property(__get_ack_code, __set_ack_code)
    err_code = property(__get_err_code, __set_err_code)
    padding = property(__get_padding, __set_padding)

    id = property(__get_id)
    total_len = property(__get_total_len)
    #endregion


    # <summary>
    # 送信データ生成
    # </summary>
    # <returns>生成データサイズ, 生成データ</returns>
    def make_send_data(self):
        len = self.total_len
        data = None

        try:
            data = [self.id] + [self.ack_code] + [self.err_code] + list(self.padding)

        except Exception as ex:
            print(ex.args)
            len = 0

        return len, data


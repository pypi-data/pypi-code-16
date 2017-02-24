# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message


# <summary>
# 音声認識コマンド送信メッセージ(0x15)
# </summary>
class MsgSendSpeechRecognitionCommand(object):
    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_ENC_FLG = 1         #暗号化フラグ
    __INDEX_LANG_CODE = 2       #ロケールID（言語コード）
    __INDEX_TIME_STAMP = 4      #タイムスタンプ(00:00:00)
    __INDEX_MODE = 12           #コマンドモード
    __INDEX_PORT = 13           #ポート番号
    __INDEX_RESERVE = 15        #予備
    __INDEX_SIZE = 20           #読み上げデータサイズ

    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #暗号化フラグ
    __ENC_FLG_OFF = 0x00           #暗号化無
    __ENC_FLG_ON = 0x01            #暗号化有
    #言語コード
    __LANG_CODE = 0x00             #ロケールID（言語コード）
    #endregion

    def __init__(self):

        self.__id = haruzira_message.MSG_SEND_SPEECH_RECOGNITION_COMMAND               #メッセージID
        self.__enc_flg = 0x00                                         #暗号化フラグ
        self.__lang_code = 0x00                                       #ロケールID（言語コード）
        self.__time_stamp = 8*[0x00]                                  #タイムスタンプ(00:00:00)
        self.__mode = 0x00                                            #コマンドモード
        self.__port = 46000                                           #ポート番号
        self.__reserve = 5*[0x00]                                     #予備
        self.__size = 0x00                                            #コマンドデータサイズ
        self.__data = None                                            #コマンドデータ（可変）
        self.__head_len = (1 * 2) + (2 + 1 * 9) + (2) + (1 * 5) + (4) #ヘッダーサイズ（読み上げデータを除いたサイズ）
        self.__total_len = 0                                          #送信フィールド合計サイズ


    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_enc_flg(self):
        return self.__INDEX_ENC_FLG

    def __get_index_lang_code(self):
        return self.__INDEX_LANG_CODE

    def __get_index_time_stamp(self):
        return self.__INDEX_TIME_STAMP

    def __get_index_mode(self):
        return self.__INDEX_MODE

    def __get_index_port(self):
        return self.__INDEX_PORT

    def __get_index_reserve(self):
        return self.__INDEX_RESERVE

    def __get_index_size(self):
        return self.__INDEX_SIZE
    #endregion

    #region アクセサ定義(送信メンバデータ値)
    def __get_enc_flg_off(self):
        return self.__ENC_FLG_OFF

    def __get_enc_flg_on(self):
        return self.__ENC_FLG_ON

    def __get_lang_code(self):
        return self.__LANG_CODE
    #endregion

    #region アクセサ定義(送信メンバ)
    def __get_id(self):
        return self.__id

    def __get_head_len(self):
        return self.__head_len

    def __get_total_len(self):
        return self.__total_len

    def __get_enc_flg(self):
        return self.__enc_flg

    def __set_enc_flg(self, enc_flg):
        self.__enc_flg = enc_flg

    def __get_lang_code(self):
        return self.__lang_code

    def __set_lang_code(self, lang_code):
        self.__lang_code = lang_code

    def __get_time_stamp(self):
        return self.__time_stamp

    def __set_time_stamp(self, time_stamp):
        self.__time_stamp = time_stamp

    def __get_mode(self):
        return self.__mode

    def __set_mode(self, mode):
        self.__mode = mode

    def __get_port(self):
        return self.__port

    def __set_port(self, port):
        self.__port = port

    def __get_reserve(self):
        return self.__reserve

    def __set_reserve(self, reserve):
        self.__reserve = reserve

    def __get_size(self):
        return self.__size

    def __set_size(self, size):
        self.__size = size

    def __get_data(self):
        return self.__data

    def __set_data(self, data):
        self.__data = data
    #endregion

    #region Property
    INDEX_ID = property(__get_index_id)
    INDEX_ENC_FLG = property(__get_index_enc_flg)
    INDEX_LANG_CODE = property(__get_index_lang_code)
    INDEX_TIME_STAMP = property(__get_index_time_stamp)
    INDEX_MODE = property(__get_index_mode)
    INDEX_PORT = property(__get_index_port)
    INDEX_RESERVE = property(__get_index_reserve)
    INDEX_SIZE = property(__get_index_size)
    ENC_FLG_OFF = property(__get_enc_flg_off)
    ENC_FLG_ON = property(__get_enc_flg_on)
    ENC_LANG_CODE = property(__get_lang_code)
    id = property(__get_id)
    head_len = property(__get_head_len)
    total_len = property(__get_total_len)
    enc_flg = property(__get_enc_flg, __set_enc_flg)
    lang_code = property(__get_lang_code, __set_lang_code)
    time_stamp = property(__get_time_stamp, __set_time_stamp)
    mode = property(__get_mode, __set_mode)
    port = property(__get_port, __set_port)
    reserve = property(__get_reserve, __set_reserve)
    size = property(__get_size, __set_size)
    data = property(__get_data, __set_data)

    #endregion

    # <summary>
    # 送信データ生成
    # </summary>
    # <param name="sd">生成データ</param>
    # <returns>生成データサイズ</returns>
    def make_send_data(self):
        self.__total_len = self.head_len + self.size
        data = None

        try:
            #ネットワークバイトオーダー(little -> big)変換後に、Byte配列に変換
            bLangCode = struct.unpack("2B", struct.pack(">H", self.lang_code))
            bPort = struct.unpack("2B", struct.pack(">H", self.port))
            bSize = struct.unpack("4B", struct.pack(">L", self.size))

            data = [self.id] + [self.enc_flg] + list(bLangCode) + list(self.time_stamp) + [self.mode] + list(bPort) + list(self.reserve) + list(bSize) + list(self.data)

        except Exception as ex:
            print(ex.args)
            self.__total_len = 0

        return (self.__total_len, data)


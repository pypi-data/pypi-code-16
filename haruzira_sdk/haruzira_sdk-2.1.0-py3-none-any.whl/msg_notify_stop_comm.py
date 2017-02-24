# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message

# <summary>
# 通信停止通知メッセージ(0x11)
# </summary>
class MsgNotifyStopComm(object):
    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_STOP_CODE = 1       #停止コード
    __INDEX_REASON_CODE = 2     #停止理由コード
    __INDEX_PADDING = 3         #アライメント


    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #応答コード
    __STOP_CODE_OK = 0x00                  #正常
    __STOP_CODE_NG = 0x01                  #異常
    #停止理由コード
    __REASON_CODE_NONE = 0x00              #通常停止
    __REASON_CODE_MAINTENANCE = 0x01       #メンテナンス（一時的な停止）
    __REASON_CODE_FAILURE = 0x02           #障害発生（恒久的な停止、復旧スケジュールが不明の場合など）
    #endregion


    def __init__(self):

        self.__id = haruzira_message.MSG_NOTIFY_STOP_COMM          #メッセージID
        self.__stop_code = 0x00                   #停止コード
        self.__reason_code = 0x00                 #停止理由コード
        self.__padding = 5*[0x00]                 #アライメント
        self.__total_len = 8                      #送信フィールド合計サイズ

    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_stop_code(self):
        return self.__INDEX_STOP_CODE

    def __get_index_reason_code(self):
        return self.__INDEX_REASON_CODE

    def __get_index_padding(self):
        return self.__INDEX_PADDING
    #endregion

    #region アクセサ定義(送信メンバデータ値)
    def __get_stop_code_ok(self):
        return self.__STOP_CODE_OK

    def __get_stop_code_ng(self):
        return self.__STOP_CODE_NG

    def __get_reason_code_none(self):
        return self.__REASON_CODE_NONE

    def __get_reason_code_maintenance(self):
        return self.__REASON_CODE_MAINTENANCE

    def __get_reason_code_failure(self):
        return self.__REASON_CODE_FAILURE
    #endregion

    #region アクセサ定義
    def __get_stop_code(self):
        return self.__stop_code

    def __set_stop_code(self, stop_code):
        self.__stop_code = stop_code

    def __get_reason_code(self):
        return self.__reason_code

    def __set_reason_code(self, reason_code):
        self.__reason_code = reason_code

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
    INDEX_STOP_CODE = property(__get_index_stop_code)
    INDEX_REASON_CODE = property(__get_index_reason_code)
    INDEX_PADDING = property(__get_index_padding)

    STOP_CODE_OK = property(__get_stop_code_ok)
    STOP_CODE_NG = property(__get_stop_code_ng)
    REASON_CODE_NONE = property(__get_reason_code_none)
    REASON_CODE_MAINTENANCE = property(__get_reason_code_maintenance)
    REASON_CODE_FAILURE = property(__get_reason_code_failure)

    stop_code = property(__get_stop_code, __set_stop_code)
    reason_code = property(__get_reason_code, __set_reason_code)
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
            data = [self.id] + [self.stop_code] + [self.reason_code] + list(self.padding)

        except Exception as ex:
            print(ex.args)
            len = 0

        return len, data

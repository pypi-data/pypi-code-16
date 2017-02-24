# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message

# <summary>
# 読み上げ完了通知メッセージ(0x13)
# </summary>
class MsgNotifyCompleteSpeech(object):
    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_RESULT = 1          #結果
    __INDEX_TIME_STAMP = 2      #タイムスタンプ(00:00:00)


    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #結果
    __RESULT_CODE_OK = 0x00                  #成功
    __RESULT_CODE_NG = 0x01                  #失敗
    #endregion


    def __init__(self):
        self.__id = haruzira_message.MSG_NOTIFY_COMPLETE_SPEECH       #メッセージID
        self.__result = self.__RESULT_CODE_OK         #結果
        self.__time_stamp = 8*[0x00]                  #タイムスタンプ(00:00:00)
        self.__total_len = 10                         #送信フィールド合計サイズ

    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_result(self):
        return self.__INDEX_RESULT

    def __get_index_time_stamp(self):
        return self.__INDEX_TIME_STAMP
    #endregion

    #region アクセサ定義(送信メンバデータ値)
    def __get_result_code_ok(self):
        return self.__RESULT_CODE_OK

    def __get_result_code_ng(self):
        return self.__RESULT_CODE_NG
    #endregion

    #region アクセサ定義
    def __get_result(self):
        return self.__result

    def __set_result(self, result):
        self.__result = result

    def __get_time_stamp(self):
        return self.__time_stamp

    def __set_time_stamp(self, time_stamp):
        self.__time_stamp = time_stamp

    def __get_id(self):
        return self.__id

    def __get_total_len(self):
        return self.__total_len
    #endregion


    #region Property
    INDEX_ID = property(__get_index_id)
    INDEX_RESULT = property(__get_index_result)
    INDEX_TIME_STAMP = property(__get_index_time_stamp)

    RESULT_CODE_OK = property(__get_result_code_ok)
    RESULT_CODE_NG = property(__get_result_code_ng)

    result = property(__get_result, __set_result)
    time_stamp = property(__get_time_stamp, __set_time_stamp)

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
            data = [self.id] + [self.result] + list(self.time_stamp)

        except Exception as ex:
            print(ex.args)
            len = 0

        return len, data

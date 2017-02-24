# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message

# <summary>
# 通信終了通知メッセージ(0x01)
# </summary>
class MsgNotifyEndComm(object):
 
    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_END_CODE = 1        #終了コード
    __INDEX_ERR_CODE = 2        #NGコード(異常時)
    __INDEX_PADDING = 3         #アライメント

    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #終了コード
    __END_CODE_OK = 0x00      #正常
    __END_CODE_NG = 0x01      #異常
    #NGコード(異常時)
    __ERR_CODE_NONE = 0x00                 #エラーなし（正常終了）
    __ERR_CODE_RCV_DATA = 0x01             #受信データエラー
    __ERR_CODE_OTHER_REASONS = 0x02        #その他原因によるエラー
    #endregion

    def __init__(self):

        self.__id = haruzira_message.MSG_NOTIFY_END_COMM             #メッセージID
        self.__end_code = 0x00                      #終了コード
        self.__err_code = 0x00                      #NGコード（異常時)
        self.__padding = 5*[0x00]                   #アライメント
        self.__total_len = 8                        #送信フィールド合計サイズ

    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_end_code(self):
        return self.__INDEX_END_CODE

    def __get_index_err_code(self):
        return self.__INDEX_ERR_CODE

    def __get_index_padding(self):
        return self.__INDEX_PADDING
    #endregion

    #region アクセサ定義(送信メンバデータ値)
    def __get_end_code_ok(self):
        return self.__END_CODE_OK

    def __get_end_code_ng(self):
        return self.__END_CODE_NG

    def __get_err_code_none(self):
        return self.__ERR_CODE_NONE

    def __get_err_code_rcv_data(self):
        return self.__ERR_CODE_RCV_DATA

    def __get_err_code_other_reasons(self):
        return self.__ERR_CODE_OTHER_REASONS
    #endregion

    #region アクセサ定義
    def __get_end_code(self):
        return self.__end_code

    def __set_end_code(self, end_code):
        self.__end_code = end_code

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
    INDEX_END_CODE = property(__get_index_end_code)
    INDEX_ERR_CODE = property(__get_index_err_code)
    INDEX_PADDING = property(__get_index_padding)

    END_CODE_OK = property(__get_end_code_ok)
    END_CODE_NG = property(__get_end_code_ng)
    ERR_CODE_NONE = property(__get_err_code_none)
    ERR_CODE_RCV_DATA = property(__get_err_code_rcv_data)
    ERR_CODE_OTHER_REASONS = property(__get_err_code_other_reasons)

    end_code = property(__get_end_code, __set_end_code)
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
            data = [self.id] + [self.end_code] + [self.err_code] + list(self.padding)

        except Exception as ex:
            print(ex.args)
            len = 0

        return len, data

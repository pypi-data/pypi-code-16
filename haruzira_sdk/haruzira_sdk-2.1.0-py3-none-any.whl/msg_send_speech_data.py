# coding: utf-8
import struct
import haruzirasdk.haruzira_message as haruzira_message

# <summary>
# 読み上げデータ送信メッセージ(0x03)
# </summary>
class MsgSendSpeechData(object):

    #region 変数・定数定義
    #メンバーIndex offset定義
    __INDEX_ID = 0              #メッセージID
    __INDEX_ENC_FLG = 1         #暗号化フラグ
    __INDEX_DATA_TYPE = 2       #データ区分(Text or SSML)
    __INDEX_PRIORITY = 3        #プライオリティ
    __INDEX_LANG_CODE = 4       #ロケールID（言語コード）
    __INDEX_GENDER = 6          #性別
    __INDEX_AGE = 7             #年齢
    __INDEX_REPEAT = 8          #リピート回数
    __INDEX_TIME_STAMP = 9      #タイムスタンプ(00:00:00)
    __INDEX_COMPLETION_NOTICE_NECESSITY = 17        #読み上げ完了通知の送信要否
    __INDEX_NAME_LEN = 18       #接続元名称サイズ
    __INDEX_SIZE = 20           #読み上げデータサイズ
    __INDEX_NAME = 24           #接続元名称(可変)

    # <summary>
    # 送信メンバデータ値定義
    # </summary>
    #暗号化フラグ
    __ENC_FLG_OFF = 0x00           #暗号化無
    __ENC_FLG_ON = 0x01            #暗号化有
    #データ区分
    __DATA_TYPE_TEXT = 0x00        #Text
    __DATA_TYPE_SSML = 0x01        #SSML
    __DATA_TYPE_TEXT_COMP = 0x10   #Text（圧縮データ）
    __DATA_TYPE_SSML_COMP = 0x11   #SSML（圧縮データ）
    #プライオリティ
    __PRIORITY_LOW = 0x00          #低い（読み上げない）
    __PRIORITY_NORMAL = 0x01       #通常（順次読み上げ）
    __PRIORITY_HIGH = 0x02         #高い（割り込み読み上げ）
    #__PRIORITY_EMARGENCY = 0x03    #緊急（最優先で割り込み読み上げ）
    #言語コード
    __LANG_LOW = 0x00          #
    #性別
    __GENDER_FEMALE = 0x00       #女性
    __GENDER_MALE = 0x01         #男性
    __GENDER_UNKNOWN = 0x02      #中性
    #性別
    #AGE_6 = 0x06               #6歳
    #繰り返し回数
    __REPEAT_NONE = 0x00           #繰り返し無
    __REPEAT_INFINITY = 0xff       #繰り返し無限
    #endregion

    def __init__(self):
 
        self.__id = haruzira_message.MSG_SEND_SPEECH_DATA              #メッセージID
        self.__enc_flg = 0x00                                          #暗号化フラグ
        self.__data_type = 0x00                                        #データ区分(Text or SSML)
        self.__priority = 0x01                                         #プライオリティ
        self.__lang_code = 0x00                                        #ロケールID（言語コード）
        self.__gender = 0x00                                           #性別
        self.__age = 0x00                                              #年齢
        self.__repeat = 0x00                                           #リピート回数
        self.__time_stamp = 8*[0x00]                                   #タイムスタンプ(00:00:00)
        self.__completion_notice_necessity = 0x00                      #読み上げ完了通知の送信要否(0x00:必要, 0x01:不要)
        self.__name_len = 0x00                                         #接続元名称サイズ
        self.__size = 0x00                                             #読み上げデータサイズ
        self.__name = None                                             #接続元名称（可変）
        self.__data = None                                             #データ（可変）
        self.__head_len = (1 * 4) + (2 + 1 * 12) + (2 + 4)             #ヘッダーサイズ（読み上げデータを除いたサイズ）
        self.__total_len = 0                                           #送信フィールド合計サイズ
    
    #region アクセサ定義(メンバーIndex offset)
    def __get_index_id(self):
        return self.__INDEX_ID

    def __get_index_enc_flg(self):
        return self.__INDEX_ENC_FLG

    def __get_index_data_type(self):
        return self.__INDEX_DATA_TYPE

    def __get_index_priority(self):
        return self.__INDEX_PRIORITY

    def __get_index_lang_code(self):
        return self.__INDEX_LANG_CODE

    def __get_index_gender(self):
        return self.__INDEX_GENDER

    def __get_index_age(self):
        return self.__INDEX_AGE

    def __get_index_repeat(self):
        return self.__INDEX_REPEAT

    def __get_index_time_stamp(self):
        return self.__INDEX_TIME_STAMP

    def __get_index_completion_notice_necessity(self):
        return self.__INDEX_COMPLETION_NOTICE_NECESSITY

    def __get_index_name_len(self):
        return self.__INDEX_NAME_LEN

    def __get_index_size(self):
        return self.__INDEX_SIZE

    def __get_index_name(self):
        return self.__INDEX_NAME
    #endregion

    #region アクセサ定義(送信メンバデータ値)
    def __get_enc_flg_off(self):
        return self.__ENC_FLG_OFF

    def __get_enc_flg_on(self):
        return self.__ENC_FLG_ON

    def __get_data_type_text(self):
        return self.__DATA_TYPE_TEXT

    def __get_data_type_ssml(self):
        return self.__DATA_TYPE_SSML

    def __get_data_type_text_comp(self):
        return self.__DATA_TYPE_TEXT_COMP

    def __get_data_type_ssml_comp(self):
        return self.__DATA_TYPE_SSML_COMP

    def __get_priority_low(self):
        return self.__PRIORITY_LOW

    def __get_priority_normal(self):
        return self.__PRIORITY_NORMAL

    def __get_priority_high(self):
        return self.__PRIORITY_HIGH

    def __get_lang_low(self):
        return self.__LANG_LOW

    def __get_gender_female(self):
        return self.__GENDER_FEMALE

    def __get_gender_male(self):
        return self.__GENDER_MALE

    def __get_gender_unknown(self):
        return self.__GENDER_UNKNOWN

    def __get_repeat_none(self):
        return self.__REPEAT_NONE

    def __get_repeat_infinity(self):
        return self.__REPEAT_INFINITY
    #endregion

    #region アクセサ定義
    def __get_enc_flg(self):
        return self.__enc_flg

    def __set_enc_flg(self, enc_flg):
        self.__enc_flg = enc_flg

    def __get_data_type(self):
        return self.__data_type

    def __set_data_type(self, data_type):
        self.__data_type = data_type

    def __get_priority(self):
        return self.__priority

    def __set_priority(self, priority):
        self.__priority = priority

    def __get_lang_code(self):
        return self.__lang_code

    def __set_lang_code(self, lang_code):
        self.__lang_code = lang_code

    def __get_gender(self):
        return self.__gender

    def __set_gender(self, gender):
        self.__gender = gender

    def __get_age(self):
        return self.__age

    def __set_age(self, age):
        self.__age = age

    def __get_repeat(self):
        return self.__repeat

    def __set_repeat(self, repeat):
        self.__repeat = repeat

    def __get_time_stamp(self):
        return self.__time_stamp

    def __set_time_stamp(self, time_stamp):
        self.__time_stamp = time_stamp

    def __get_completion_notice_necessity(self):
        return self.__completion_notice_necessity

    def __set_completion_notice_necessity(self, necessity):
        self.__completion_notice_necessity = necessity

    def __get_name_len(self):
        return self.__name_len

    def __set_name_len(self, name_len):
        self.__name_len = name_len

    def __get_size(self):
        return self.__size

    def __set_size(self, size):
        self.__size = size

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_data(self):
        return self.__data

    def __set_data(self, data):
        self.__data = data

    def __get_id(self):
        return self.__id

    def __get_head_len(self):
        return self.__head_len

    def __get_total_len(self):
        return self.__total_len
    #endregion


    #region Property
    INDEX_ID = property(__get_index_id)
    INDEX_ENC_FLG = property(__get_index_enc_flg)
    INDEX_DATA_TYPE = property(__get_index_data_type)
    INDEX_PRIORITY = property(__get_index_priority)
    INDEX_LANG_CODE = property(__get_index_lang_code)
    INDEX_GENDER = property(__get_index_gender)
    INDEX_AGE = property(__get_index_age)
    INDEX_REPEAT = property(__get_index_repeat)
    INDEX_TIME_STAMP = property(__get_index_time_stamp)
    INDEX_COMPLETION_NOTICE_NECESSITY = property(__get_index_completion_notice_necessity)
    INDEX_NAME_LEN = property(__get_index_name_len)
    INDEX_SIZE = property(__get_index_size)
    INDEX_NAME = property(__get_index_name)

    ENC_FLG_OFF = property(__get_enc_flg_off)
    ENC_FLG_ON = property(__get_enc_flg_on)
    DATA_TYPE_TEXT = property(__get_data_type_text)
    DATA_TYPE_SSML = property(__get_data_type_ssml)
    DATA_TYPE_TEXT_COMP = property(__get_data_type_text_comp)
    DATA_TYPE_SSML_COMP = property(__get_data_type_ssml_comp)
    PRIORITY_LOW = property(__get_priority_low)
    PRIORITY_NORMAL = property(__get_priority_normal)
    PRIORITY_HIGH = property(__get_priority_high)
    LANG_LOW = property(__get_lang_low)
    GENDER_FEMALE = property(__get_gender_female)
    GENDER_MALE = property(__get_gender_male)
    GENDER_UNKNOWN = property(__get_gender_unknown)
    REPEAT_NONE = property(__get_repeat_none)
    REPEAT_INFINITY = property(__get_repeat_infinity)

    enc_flg = property(__get_enc_flg, __set_enc_flg)
    data_type = property(__get_data_type, __set_data_type)
    priority = property(__get_priority, __set_priority)
    lang_code = property(__get_lang_code, __set_lang_code)
    gender = property(__get_gender, __set_gender)
    age = property(__get_age, __set_age)
    repeat = property(__get_repeat, __set_repeat)
    time_stamp = property(__get_time_stamp, __set_time_stamp)
    completion_notice_necessity = property(__get_completion_notice_necessity, __set_completion_notice_necessity)
    name_len = property(__get_name_len, __set_name_len)
    size = property(__get_size, __set_size)
    name = property(__get_name, __set_name)
    data = property(__get_data, __set_data)

    id = property(__get_id)
    head_len = property(__get_head_len)
    total_len = property(__get_total_len)
    #endregion


    # <summary>
    # 送信データ生成
    # </summary>
    # <returns>生成データサイズ, 生成データ</returns>
    def make_send_data(self):
        self.__total_len = self.head_len + self.name_len + self.size
        mdata = None
        
        try:
            #ネットワークバイトオーダー後に、Byte配列に変換
            bLangCode = struct.unpack("2B", struct.pack(">H", self.lang_code))
            bNameLen = struct.unpack("2B", struct.pack(">H", self.name_len))
            bSize = struct.unpack("4B", struct.pack(">L", self.size))

            if self.__name is not None:
                mdata = [self.id] + [self.enc_flg] + [self.data_type] + [self.priority] + list(bLangCode) + [self.gender] + [self.age] + [self.repeat] + list(self.time_stamp) + [self.completion_notice_necessity] + list(bNameLen) + list(bSize) + list(self.name) + list(self.data)
            else:
                mdata = [self.id] + [self.enc_flg] + [self.data_type] + [self.priority] + list(bLangCode) + [self.gender] + [self.age] + [self.repeat] + list(self.time_stamp) + [self.completion_notice_necessity] + list(bNameLen) + list(bSize) + list(self.data)

        except Exception as ex:
            print(ex.args)
            self.__total_len = 0

        return self.__total_len, mdata

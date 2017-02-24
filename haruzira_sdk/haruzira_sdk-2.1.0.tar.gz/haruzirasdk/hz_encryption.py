# coding: utf-8
from enum import Enum
from Crypto.Cipher import AES
#from pkcs7 import PKCS7Encoder
import struct
import numpy as np

#region enum
# <summary>
# スピーチモード
# </summary>
class EncryptionType(Enum):
    AesCbc = 0
    AesCbcPkcs7 = 1
#endregion

HZ_XOR_VALUE = 0xb7

class Encryption(object):

    def __init__(self):
        #region 変数・定数
        self.__BLOCK_SIZE = 16
        #endregion


    # <summary>
    # キーの生成（AES-CBC）
    # </summary>
    # <param name="strMsg">s生成を行うキー文字列</param>
    # <returns>生成されたキー文字列</returns>
    def __createKey(self, k):
        retKey = k
        lack = len(retKey) % self.__BLOCK_SIZE
        #puts lack
        if(lack != 0):
            i = 0
            j = 0
            while i < (self.__BLOCK_SIZE - lack):
                retKey = retKey + str(j)
                i += 1
                if(j < 9):
                    j += 1
                else:
                    j = 0

        #puts retKey
        return retKey

    # <summary>
    # Padding(PKCS#7)
    # </summary>
    # <param name="str_data">暗号化を行う文字列</param>
    # <returns>Paddingされた文字列</returns>
    def _pad_pkcs7(self, str_data):
        data_len = len(str_data)
        pad_len = self.__BLOCK_SIZE - (data_len % self.__BLOCK_SIZE)
        js = pad_len * chr(pad_len)
        return str_data + js.encode("utf-8")
    
    # <summary>
    # UnPadding(PKCS#7)
    # </summary>
    # <param name="str_data">Paddingされた字列</param>
    # <returns>Paddingを削除した文字列</returns>
    def _unpad_pkcs7(self, str_data):
        data_len = len(str_data)
        pad_len = str_data[-1]
        if pad_len > self.__BLOCK_SIZE:
            return None
        return str_data[:data_len - pad_len]

    # <summary>
    # 文字列の暗号化（AES-CBC）
    # </summary>
    # <param name="strMsg">暗号化を行う文字列</param>
    # <param name="encType">暗号化のアルゴリズム</param>
    # <param name="strEncKey">暗号化キー文字列</param>
    # <returns>暗号化されたbyte配列</returns>
    def cipherEncryption(self, strMsg, encType, strEncKey):
        #enc_data = ""

        try:
            key = self.__createKey(strEncKey)
            iv = self.reverseString(key)
            enc = AES.new(key, AES.MODE_CBC, iv)
            pad_data = self._pad_pkcs7(strMsg)
            if(pad_data is None):
                raise ValueError("Failed padding by pkcs#7.")

            enc_data = enc.encrypt(pad_data)

        except Exception as ex:
            print(ex.args)
            enc_data = ""
        finally:
            return struct.unpack("{}B".format(len(enc_data)), enc_data)

    # <summary>
    # 文字列の複合化(AES-CBC)
    # </summary>
    # <param name="decType">複合化のアルゴリズム</param>
    # <param name="byteDecrypt">複合対象文字列</param>
    # <param name="strDecKey">複合キー文字列</param>
    # <returns>OK:複合化された文字列,NG:""</returns>
    def cipherDecryption(self, decType, byteDecrypt, strDecKey):
        dec_data = ""

        try:
            key = self.__createKey(strDecKey)
            iv = self.reverseString(key)
            dec = AES.new(key, AES.MODE_CBC, iv)
            dec_data = dec.decrypt(byteDecrypt)
            ret_data = self._unpad_pkcs7(dec_data)

        except Exception as ex:
            print(ex.args)
            ret_data = ""
        finally:
            return ret_data
            

    # <summary>
    # 文字列を反転する
    # </summary>
    # <param name="strBuff">反転対象文字列</param>
    # <returns>反転結果</returns>
    def reverseString(self, strBuff):
        rvsStr = strBuff[::-1].encode("utf-8")
        i = 0
        retBuf = []
        #retBuf = None
        for b in rvsStr:
            retBuf = retBuf + [b ^ HZ_XOR_VALUE]
            if(i > 15):
                break
            else:
                i = i + 1

        return np.array(retBuf, dtype=np.uint8)

    # <summary>
    # Base64にエンコードする
    # </summary>
    # <param name="buff">エンコード対象文字列バイト配列</param>
    # <returns>エンコード結果</returns>
    def encodeToBase64String(self, buff):
        strBase64 = Base64.encode64(struct.pack("s", buff))

        return strBase64


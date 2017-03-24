# encoding: utf-8
import os

from M2Crypto import RSA

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

RSA_PRIV_KEY_PATH = BASE_DIR + "/net/privkey.pem"
RSA_PUB_KEY_PATH = BASE_DIR + "/net/pubkey.pem"


class RsaUtil():
    def encrypt(self, data):
        '''
        加密或者解密
        @param data: 要加密或者解密的数据
        @param is_encrypt: 加密操作或者解密操作（加密：True，解密：False）
        @return: 加密或者解密后的数据
        '''
        rsa_pub = RSA.load_pub_key(RSA_PUB_KEY_PATH)
        rsa_len = 117
        if len(data) > rsa_len:
            tmp = ''
            for i in range(len(data) / rsa_len + 1):
                t = data[i * rsa_len:(i + 1) * rsa_len]
                tmp += rsa_pub.public_encrypt(t, RSA.pkcs1_padding)
                print len(tmp), tmp
            return tmp
        else:
            return rsa_pub.public_encrypt(data, RSA.pkcs1_padding)

    def decrypt(self, data):
        rsa_len = 128
        rsa_pri = RSA.load_key(RSA_PRIV_KEY_PATH)
        tmp = ''
        for i in range(len(data) / rsa_len):
            t = data[i * rsa_len:(i + 1) * rsa_len]
            tmp += rsa_pri.private_decrypt(t, RSA.pkcs1_padding)
        return tmp

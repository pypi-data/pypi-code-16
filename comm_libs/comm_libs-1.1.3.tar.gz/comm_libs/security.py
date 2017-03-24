#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import base64
import hashlib

import OpenSSL
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA


class RsaEncryptor(object):
    """Rsa加解密实现类

    公钥格式必须是 pkcs#8 pem
    私钥格式必须是 x509 der

    Example:
        rsa_encryptor = security.RsaEncryptor("d:/public_key.der", "d:/private_key.pk8")

        param_dict = {
        'name' : 'hello',
        'pass' : '123',
        'date' : '2012-12-12 00:00:00'
        }

        # 生成参数签名
        sig = rsa_encryptor.sign(param_dict)

        #检查签名
        print rsa_encryptor.check_sign(param_dict, sig)


    Attributes:
        pubkey_path (str): 公钥文件路径
        prikey_path (str): 私钥文件路径
    """
    def __init__(self, pubkey_path = None, prikey_path = None,
                 pubkey_bytes = None, prikey_bytes = None):
        if (not pubkey_path and not pubkey_bytes)  or (not prikey_path and not prikey_bytes):
            raise RsaEncryptorException("初始化失败，找不到密钥文件！")

        pubkey_der = None
        pubkey_pk8 = None

        if pubkey_path and prikey_path:
            # 加载公钥
            pubkey_der = open(pubkey_path, 'rb').read()
            # 加载私钥
            pubkey_pk8 = open(prikey_path, 'rb').read()
        elif pubkey_bytes and prikey_bytes:
            pubkey_der = pubkey_bytes
            pubkey_pk8 = prikey_bytes
            pass
        else:
            raise RsaEncryptorException("初始化失败找，不到密钥文件!")

        # 转换公钥格式DER为PEM
        pubkey = OpenSSL.crypto.load_publickey(OpenSSL.crypto.FILETYPE_ASN1, pubkey_der)
        pem_pubkey = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pubkey)

        # 公钥
        self.__pubkey = RSA.importKey(pem_pubkey)
        # 私钥
        self.__prikey = RSA.importKey(pubkey_pk8)

    def encrypt(self, plaintxt):
        """使用rsa公钥对文本进行加密返回文本是经过BASE64编码过的
        Args:
            plaintxt (str): 需要加密的原文
        Returns:
            str: Base64编码的密文
        """
        raw_bytes = self.__pubkey.encrypt(plaintxt, 32)[0]

        return base64.encodestring(raw_bytes)

    def decrypt(self, ciphertxt):
        """使用rsa私钥对加密文本进行解密
        Args:
            ciphertxt (str): 经过base64编码的密文
        Returns:
            str: 原文
        """
        raw_bytes = base64.decodestring(ciphertxt)
        return self.__prikey.decrypt(raw_bytes)


    def sign(self, params_dict):
        """使用rsa私钥对参数进行签名
        Args:
            params_dict (dict): 需要签名的参数字典 eg.{'name': 'li', 'password': '123456'}
        Returns:
            str: 签名
        """
        param_str = self.concat_params(params_dict)

        digest = self.md5digest(param_str)

        signer = PKCS1_v1_5.new(self.__prikey)

        h = SHA.new(digest)

        sign = signer.sign(h)

        return base64.encodestring(sign)

    def check_sign(self, params_dict, signature):
        """使用rsa公钥对签名进行验证
        Args:
            params_dict (dict): 待验证参数字典
            signature (str): 参数签名
        Returns:
            bool: true 通过 false 不通过
        """

        param_str = self.concat_params(params_dict)
        digest = self.md5digest(param_str)

        verifier = PKCS1_v1_5.new(self.__pubkey)

        h = SHA.new(digest)

        return verifier.verify(h, base64.decodestring(signature))

    def concat_params(self, params_dict):
        """将参数字典以key=value&key2=value2的形式凭借
        Args:
            params_dict (dict): 参数字典
        Returns:
            str: 拼接后的参数字符串
        """
        keys = params_dict.keys()
        keys.sort()

        param_str = ''
        for i in keys:
            if not param_str:
                param_str += '%s=%s' % (i, params_dict[i])
            else:
                param_str += '&%s=%s' % (i, params_dict[i])

        return param_str

    def md5digest(self, txt):
        """md5摘要方法
        Args:
            txt (str): 需要处理的文本
        Returns:
            str: 摘要信息
        """
        md5 = hashlib.md5()
        md5.update(txt)
        return md5.hexdigest()


class RsaEncryptorException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
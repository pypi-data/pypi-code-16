# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from fcrypter.base.templates import Cryptor


class AESCryptorEAX(Cryptor):
    """
    AES EAX mode file encryption through use of pycryptodome AES library

    For details, see
        https://en.wikipedia.org/wiki/EAX_mode
        http://web.cs.ucdavis.edu/~rogaway/papers/eax.pdf
    """
    def __init__(self):
        super(AESCryptorEAX, self).__init__(tuple([16, 24, 32]))

    @staticmethod
    def _write_crypto(finput, foutput, crypt_action):
        while True:
            txt = finput.read(1024)
            if not txt:
                break
            foutput.write(crypt_action(txt))

    def encrypt_file(self, key, f_path, encr_fpath):
        """
        Encrypts files, then digests.
        Provides plaintext & ciphertext integrity

        More info about "Encrypt then MAC" in Bellare & Namprempre paper:

            Authenticated Encryption: Relations among notions
            and analysis of the generic composition paradigm

            http://cseweb.ucsd.edu/~mihir/papers/oem.pdf

        Since AES library doesn't provide easy way to do this in seperate
        actions we add 16 dummy bytes as MAC, write the encrypted content
        and then seek the dummy bytes and overwrite with the correct MAC

        This allows us to read a file for encryption in small chunks to avoid
        insufficient memory errors
        """
        self.verify_supported_key_size(key)
        cipher = AES.new(key, AES.MODE_EAX)
        with open(f_path, "rb") as fin, open(encr_fpath, "wr+b") as fout:
            fout.write(cipher.nonce)
            fout.write(get_random_bytes(16))
            self._write_crypto(fin, fout, cipher.encrypt)
            fout.seek(16)
            fout.write(cipher.digest())

    def decrypt_file(self, key, encr_fpath, decr_fpath):
        """
        Decrypts file and verifies integrity
        """
        self.verify_supported_key_size(key)
        with open(encr_fpath, "rb") as fin, open(decr_fpath, "wb") as fout:
            nonce, tag = [fin.read(x) for x in (16, 16)]
            cipher = AES.new(key, AES.MODE_EAX, nonce)
            self._write_crypto(fin, fout, cipher.decrypt)
            cipher.verify(tag)

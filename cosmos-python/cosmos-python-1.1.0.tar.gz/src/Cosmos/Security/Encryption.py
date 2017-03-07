import base64
import binascii
import Cryptodome
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA
from Cryptodome import Random
from Cryptodome.Util.Padding import unpad


class Encryption:

    @staticmethod
    def decrypt(enc_body, enc_cipher, cosmos):
        apiKey = cosmos.getApiKey()
        privateKey = base64.b64decode(cosmos.getPrivateKey())
        enc_cipher = binascii.a2b_hex(enc_cipher)

        key = RSA.importKey(privateKey)
        cipher = PKCS1_v1_5.new(key)

        dsize = SHA.digest_size
        sentinel = Random.new().read(dsize+10)

        myCipher = cipher.decrypt(enc_cipher, sentinel).decode()

        aes = AES.new(bytes(apiKey[:16], "utf-8"), AES.MODE_CBC, bytes(myCipher, "utf-8"))
        enc_body = binascii.a2b_hex(enc_body)
        res = unpad(aes.decrypt(enc_body), 16).decode()

        return res

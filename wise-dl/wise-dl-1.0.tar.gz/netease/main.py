# coding= utf-8
import binascii
from Crypto.Cipher import AES
import json
import base64
import os
import sys
import requests

directory = r"E:\网易云音乐"

#  function d(d, e, f, g)
BS = AES.block_size  # aes數據分組長度為128 bit BS = 16

# 填充方式为pkcs7
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

bl = {
    'br': 320000,
    'csrf_token': "18d55720a342bf3eae987e7ca40a5ed4",
    'ids': "[28228208]"
}

p1 = json.dumps(bl)

p2 = '010001'  # rsa pubkey

# modulus rsa系数
p3 = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'

p4 = '0CoJUm6Qyw8W8jud'  # aes key

iv = '0102030405060708'  # aes 向量


# 生成size位随机字符
def createSecretKey(size):
    return ''.join([hex(x)[2:] for x in os.urandom(size)])[0:16]


def AES_encrypt(text, key, iv):
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_rlt = cryptor.encrypt(pad(text))
    rlt = base64.b64encode(encrypt_rlt)
    # print(type(rlt))

    return rlt.decode()  # decode默认解码方式为ascii,py3中，base64编码后默认仍是二进制数据


def get_params(text, rnd):
    params = AES_encrypt(text, p4, iv)
    params = AES_encrypt(params, rnd, iv)
    return params


# pubKey = p2 modulus = p3
def get_encSecKey(text, pubKey, modulus):
    text = text[::-1].encode()
    rs = int(binascii.hexlify(text), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)

    params = get_params(text, secKey)
    encSecKey = get_encSecKey(secKey, p2, p3)

    data = {
        'params': params,
        'encSecKey': encSecKey
    }
    return data


def download(url, song_id):
    songInfoUrl = r"http://music.163.com/api/song/detail/?ids=%5B{}%5D".format(song_id)

    # 这里要对text的编码作出申明，默认是gbk，那么遇到譬如韩文则会报错
    rlt = requests.get(songInfoUrl)
    # tmp = rlt.content.decode('utf-8')
    # print(tmp)
    songName = json.loads(rlt.text)['songs'][0]['name']
    # 如果你本身拿到的是utf - 8等，非gbk编码的字符串，然后用print去打印出来在windows系统就是输出到cmd中
    # 而cmd中，（对于多数中国人所用的是中文的系统）默认字符编码是gbk.从而print导致此种现象：
    # print(songName)   取消注释报错
    print('Start to download song ...')
    r = requests.get(url)
    with open(directory + '\{}.mp3'.format(songName), 'wb') as f:
        f.write(r.content)
    print('Finished ...')


def run():
    global bl,directory
    if sys.argv[1] == '-i' and len(sys.argv) == 3:
        song_id = sys.argv[2]
        bl['ids'] = "[{}]".format(song_id)
    elif sys.argv[1] == '-d' and len(sys.argv) == 3:
        directory = sys.argv[2]
        print('Edit Success')
        sys.exit(0)

    else:
        print('Params Error')
        sys.exit(1)

    data = encrypted_request(bl)
    # print(data)
    url = r"http://music.163.com/weapi/song/enhance/player/url?csrf_token=18d55720a342bf3eae987e7ca40a5ed4"
    rlt = requests.post(url, data=data)
    print(rlt.text)
    download_url = json.loads(rlt.text)['data'][0]['url']
    print('Get the song download url :' + download_url)
    download(download_url, song_id)


if __name__ == "__main__":
    run()

# -*- coding: utf-8 -*-
import os
from zipfile import ZipFile
import hashlib
import shutil


def md5hash_file(filepath):
    """ Calculating md5 hash for the the file at `filepath` """

    BUF_SIZE = 65536
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


class Archive(object):

    def __init__(self, file_or_dir_path):

        self.path = os.path.expanduser(file_or_dir_path)
        self.ar_path = self.path + '.zip'

    def compress(self):

        assert os.path.exists(self.path)
        with ZipFile(self.ar_path, mode='w') as zipf:
            if os.path.isfile(self.path):
                zipf.write(self.path, os.path.basename(self.path))
            else:
                assert os.path.isdir(self.path)
                shutil.make_archive(self.ar_path, 'zip', self.path)

        self.checksum = md5hash_file(self.ar_path)

    def split(self, split_size=500000):

        assert os.path.isfile(self.ar_path)
        data = ''
        count = 0
        with open(self.ar_path, 'rb') as f:
            while 1:
                b = f.read(1)
                if b == '':
                    yield data.encode('base64')
                    return

                count += 1
                data += b
                if count >= split_size:
                    yield data.encode('base64')
                    count = 0
                    data = ''

    def remove(self):
        os.remove(self.ar_path)

    def decompress(self):
        assert os.path.isfile(self.ar_path)
        with ZipFile(self.ar_path, mode='r') as zipf:
            zipf.extractall()

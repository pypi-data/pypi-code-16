
import os
import requests
import sys
from wcs.commons.config import PUT_URL
from wcs.commons.http import _post
from wcs.commons.util import get_logger
from wcs.commons.util import urlsafe_base64_decode
from wcs.commons.config import logging_folder
from poster.encode import multipart_encode

class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = iterable.total

    def read(self, size=-1): 
        return next(self.iterator, b'')

    def __len__(self):
        return self.length

def progress(param, current, total):
    if not param:
        return
    progress =  "{0} ({1}) - {2:d}/{3:d} - {4:.2f}%".format(param.name, param.filename, current, total, float(current)/float(total)*100)
    print(progress)

def multipart_encode_for_requests(params, boundary=None, cb=None):
    datagen, headers = multipart_encode(params, boundary, cb)
    return IterableToFileAdapter(datagen), headers

class RegUpload(object):

    def __init__(self,uploadtoken):
        self.fileds = {"token":uploadtoken}
        self.logger = get_logger(logging_folder, 'regupload')
        
    def reg_upload(self, filepath):
        puturl = "{0}/{1}/{2}".format(PUT_URL,"file","upload")
        if os.path.exists(filepath) and os.path.isfile(filepath):
            filedir,filename = os.path.split(filepath)
            self.fileds['file'] = open(filepath, 'rb')
        else:
            self.logger.error('Please input a existing file')
            return -1, 'Sorry ! We need a existing file to upload\n'
        datagen, headers = multipart_encode_for_requests(self.fileds, cb=progress)     
        headers['Accept'] = "*/*"
        try:
            self.logger.info('File %s upload progress start!', filepath)
            r = requests.post(url=puturl, headers=headers, data=datagen)
        except Exception as e:
            self.logger.error('There is exception:%s in upload progress', e)
            return -1, e
        self.logger.info('The result of upload is: %d, %s', r.status_code, r.text)
        # user need to decode text by itself, for text may be json,for example in callback upload
        #if r.status_code == 200:
        #    return r.status_code, urlsafe_base64_decode(r.text)
        #else:
        #    return r.status_code, r.text
        return r.status_code, r.text


import os
import requests
import sys
from wcs.commons.config import PUT_URL
from wcs.commons.http import _post
from wcs.commons.util import get_logger
from wcs.commons.util import urlsafe_base64_decode
from wcs.commons.config import logging_folder


class RegUpload(object):

    def __init__(self,uploadtoken):
        self.fileds = {"token":uploadtoken}
        self.logger = get_logger(logging_folder, 'regupload')
        
    def reg_upload(self, filepath):
        puturl = "{0}/{1}/{2}".format(PUT_URL,"file","upload")
        if os.path.exists(filepath) and os.path.isfile(filepath):
            f = open(filepath, 'rb')
            file = {'file': f}
            headers = {"Accept":"*/*"}
            try:
                self.logger.info('File %s upload start!', filepath)
                r = requests.post(url=puturl, headers=headers, data=self.fileds, files=file, verify=True)
            except Exception as e:
                self.logger.error('There is exception:%s in upload progress', e)
                f.close()
                return -1, e
            f.close()
            self.logger.info('The result of upload is: %d, %s', r.status_code, r.text)
            return r.status_code, r.text
        else:
            self.logger.error('Please input a existing file')
            return -1, 'Sorry ! We need a existing file to upload\n'

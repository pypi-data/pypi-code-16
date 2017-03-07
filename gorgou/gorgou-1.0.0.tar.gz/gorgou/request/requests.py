#!/usr/bin/env python
# -*-encoding:utf-8-*-

import os
import requests


def download_file(source_url, dest_file):
    r = requests.get(source_url)
    if r.status_code == 200:
        f = open(dest_file, 'wb')
        f.write(r.content)
        f.close()


def download_file2(source_url, dest_file):
    pdir = os.path.dirname(dest_file)
    if not os.path.exists(pdir):
        os.makedirs(pdir)
    download_file(source_url, dest_file)


def upload_file(source_file, dest_url):
    # Request URL:http://192.168.1.100:8899/scripts/uploadify.html
    # Request Headers
    # Provisional headers are shown
    # Content-Type:multipart/form-data; boundary=----------Ij5gL6cH2GI3Ef1ae0ei4Ef1ae0gL6
    # Origin:http://192.168.1.100:8899
    # Referer:http://192.168.1.100:8899/
    # User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36
    # X-Requested-With:ShockwaveFlash/21.0.0.197
    # Request Payload
    # ------------Ij5gL6cH2GI3Ef1ae0ei4Ef1ae0gL6
    # Content-Disposition: form-data; name="Filename"
    #
    # 谜一样的双眼.rmvb
    # ------------Ij5gL6cH2GI3Ef1ae0ei4Ef1ae0gL6
    # Content-Disposition: form-data; name="Filedata"; filename="谜一样的双眼.rmvb"
    # Content-Type: application/octet-stream
    #
    #
    # ------------Ij5gL6cH2GI3Ef1ae0ei4Ef1ae0gL6
    # Content-Disposition: form-data; name="Upload"
    #
    # Submit Query
    # ------------Ij5gL6cH2GI3Ef1ae0ei4Ef1ae0gL6--
    n = os.path.basename(source_file)
    f = open(source_file, 'rb')
    c = "application/octet-stream"
    requests.post(dest_url, files={"Filedata": (n, f, c)})

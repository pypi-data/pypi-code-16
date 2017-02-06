# -*- encoding: utf-8 -*-

import json
import logging
import logging.handlers
import requests
import urllib.request, urllib.parse, urllib.error

from .utils import *
# from Templates import Templates

class BestSignAPI(object):
    def __init__(self, url, mid, private_key, timeout=120, log_file=None,
                 log_level=logging.DEBUG, api_version='1.3.0'):
        self.url = url
        self.mid = mid
        self.private_key = private_key
        self.timeout = timeout
        self.log_file = log_file
        self.log_level = log_level
        self.api_version = '1.3.0'
        self.sucess_code = [200, 201, 203]
        
        logger = logging.getLogger(__name__)
        
        if log_file:
            handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
        else:
            handler = logging.StreamHandler()
            
        handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        
        logger.info("Initialize BestSign Python SDK OK!")
    
    def set_timeout(self, timeout):
        self.logger.debug("Set timeout [{0}] -> [{1}]".format(self.timeout, timeout))
        self.timeout = timeout
    
    def _post(self, request_url, headers, post_data):
        # r = requests.post(request_url, headers=headers, data=post_data, verify=False)
        r = requests.post(request_url, headers=headers, data=post_data)
        if r.status_code in self.sucess_code:
            self.logger.info("BestSign API response: \n{0}\n".format(r.text))
            return r.text
        else:
            self.logger.error("POST data to [{0}] failed!".format(request_url))
            self.logger.debug("HTTP code: {0}\nHTTP data: {1}".format(r.status_code, r.text))
            
    def post_request(self, method, path, content): 
        self.logger.info("Request API path: [{0}]".format(path))
        if self.log_file:
            self.logger.debug("POST Data: \n{0}\n".format(shorten_long_dict(content)))
        
        post_content = {"request": {"content": content}}
        post_data = json.dumps(post_content)
        
        sign_data = get_sign_data(method, self.mid, md5_encode(post_data))
        
        return self._execute(path, 'POST', post_data, sign_data)

    def _execute(self, api_path, method='POST', post_data=None, sign_data='', header_data={}, auto_redirect=True):
        request_url = self.url + api_path
        if post_data is None:
            raise ValueError('post data is None')
        
        sign = get_rsa_sign(sign_data, self.private_key)
        header_data['mid'] = self.mid
        header_data['sign'] = urllib.parse.quote(sign)
        header_data['User-Agent'] = 'BestSign/SDK/Python3/1.3.0'
        header_data['Content-Type'] = 'application/json; charset=UTF-8'
        header_data['Cache-Control'] = 'no-cache'
        header_data['Pragma'] = 'no-cache'
        header_data['Connection'] = 'keep-alive'

        # print('execute headers=>' + str(header_data))

        if 'POST' == method.upper():
            return self._post(request_url, header_data, post_data)
        elif 'GET' == method.upper():
            print('GET')
    
    def register_user(self, user):
        """
        Register a new user on BestSign Cloud Platform.
        
        Parameters
        ----------
        user : a dict contains user information.
        
        {
            'email': '',
            'mobile': '<MUST>',
            'name': '<MUST>',
            'userType': '<MUST>'
        }

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'regUser.json'
        path = '/open/' + method
        
        return self.post_request(method, path, user)
    
    def upload_user_image(self, image, user, update="1", seal_name=None, seal_type=None):
        """
        Upload an image to BestSign. The image will be used as sign/seal.
        
        Parameters
        ----------
        image : file path of image.
        user : a dict contains user information.
        
        {
            'useracount': '<MUST>',
            'usermobile': '',
            'usertype': '<MUST>',
            'username': '<MUST>'
        }
        
        update : if "1", the new image will replace the old one.
        seal_name : a name for seal if have more than one seal.
        seal_type : "1" is mainland seal, "2" is HongKong seal.

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'uploaduserimage.json'
        path = '/open/' + method
        
        content = user
        content['imgName'] = get_file_name(image)
        content['image'] = file_to_stream(image).decode('ascii')
        content['imgtype'] = get_file_ext(image)
        content['updateflag'] = update
        if seal_name:
            content['sealname'] = seal_name
        if seal_type:
            content['sealImageType'] = seal_type
        
        return self.post_request(method, path, content)
    
    def query_user_image(self, user_account, seal_name=None):
        """
        Query sign/seal for a user.
        
        Parameters
        ----------
        user_account : a mobile or an email.
        seal_name : the name of seal. if None return the default one.

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'queryuserimage.json'
        path = "/open/" + method
        
        content = {
            'useracount': user_account
        }
        if seal_name:
            content['sealname'] = seal_name
        
        return self.post_request(method, path, content)

    def apply_personal_certificate(self, personal_user):
        """
        Apply a personal certificate for user.
        
        Parameters
        ----------
        personal_user : a dict contains user information for certificate applying.
        
        {
            'userType': '<MUST>',
            'name': '<MUST>',
            'password': '<MUST>', #  for example "123456"
            'identityType': '<MUST>',
            'identity': '<MUST>',
            'province': '<MUST>',
            'city': '<MUST>',
            'address': '<MUST>',
            'duration': "24", # 1 - 36 months
            'mobile': '<MUST>',
            'email': ''
        }

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'certificateApply.json'
        path = '/open/' + method
        
        return self.post_request(method, path, personal_user)
    
    def apply_enterprise_certificate(self, ent_user):
        """
        Apply an enterprise certificate for corporate user.
        
        Parameters
        ----------
        ent_user : a dict contains corporate information for certificate applying.
        
        {
            'userType': '<MUST>',
            'name': '<MUST>',
            'password': '<MUST>', #  for example "123456"
            'linkMan': '<MUST>',
            'linkIdCode': '<MUST>',
            'icCode': '<MUST>',
            'orgCode': '<MUST>',
            'taxCode': '<MUST>',
            'province': '<MUST>',
            'city': '<MUST>',
            'address': '<MUST>',
            'duration': "24", # 1 - 36 months
            'mobile': '<MUST>',
            'email': ''
        }

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'certificateApply.json'
        path = '/open/' + method
        
        return self.post_request(method, path, ent_user)
    
    def send_document(self, document, sponsor, *signatories):
        """
        Send out a document and specify signatories.
        
        Parameters
        ----------
        document : file path of the document need to sign.
        sponsor : a dict contains sponsor information of the document.
        
        {
            "email":"",                 # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
                                        # to generate a virtual mailbox.
            "emailtitle": "<MUST>",     # Must
            "emailcontent": "",         # Optional,can be empty
            "sxdays": "3",              # Optional,default value 3 day
            "selfsign": "1",            # 0: No need self-sign,1:Need self-sign
            "name": "<MUST>",           # Must
            "mobile": "<MUST>",         # Must
            "usertype": "<MUST>",       # Must, 1: Individual ,2:Enterprise
            "Signimagetype": "1",       # 0:Not generated to default Sign image.1:Generated to default Sign image
            "UserfileType": "1"         # 1: upload file from local, 2: use cloud file
        }
        
        signatories : one or more dict contains signatory information of the document.
        
        {
            "email": "",                # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
            "name": "<MUST>",
            "isvideo": '0',             # 1:yes, 0:no, 2:two-way,
            "mobile": "<MUST>",
            "usertype": "<MUST>",       # Must, 1: user,2:Enterprise
            "Signimagetype": "1",       # 0:Not generated to default Sign image.1:Generated to default Sign image
        }

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'sjdsendcontractdocUpload.json'
        path = '/open/' + method
        
        spo_str = json.dumps([sponsor])
        sig_list = []
        for i in signatories:
            sig_list.append(i)
        if sig_list:
            sig_str = json.dumps(sig_list)
        else:
            sig_str = ''
        
        file_name = get_file_name(document)
        
        file_type = sponsor['UserfileType']
        if file_type == '1':
            file_data = file_to_stream(document, base64_encode=False)
            md5sum = md5_encode(file_data)
            sub_data = get_sign_data(md5sum, file_name, sig_str, spo_str)
            
        elif file_type == '2':
            sub_data = get_sign_data(sig_str, spo_str)
        else:
            raise ValueError("DO NOT support file type [{0}]".format(file_type))
        
        sign_data = get_sign_data(method, self.mid, sub_data)
        
        headers = {}
        headers['userlist'] = sig_str
        headers['senduser'] = spo_str
        headers['filename'] = file_name
        
        self.logger.info("API path: [{0}]".format(path))
        self.logger.debug("POST headers: \n{0}\n".format(headers)) 
        return self._execute(path, post_data=file_data, sign_data=sign_data, header_data=headers)
    
    def append_signatory(self, sign_id, *signatories):
        """
        Add new signatories for a document signing.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
        
        signatories : one or more dict contains signatory information.
        
        {
            'name': '<MUST>',
            'mobile': '<MUST>',
            'email': '',
            'usertype': '<MUST>',
            'isvideo': '0',
            'Signimagetype' : '1'
        }

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'sjdsendcontract.json'
        path = '/open/' + method
        
        user_list = []
        for i in signatories:
            user_list.append(i)
            
        content = {
            'signid': sign_id,
            'userlist': user_list
        }
        
        return self.post_request(method, path, content)
    
    def auto_sign(self, sign_id, user_account, sign_positions, auto_complete="1",
                  seal_name=None, notice_url=None):
        """
        Automatically sign off the document.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
        user_account : a mobile or an email.
        sign_positions : a list contains sign positions.
        
        [
            {'pagenum': '1', 'signx': '0.5', 'signy': '0.5'},
            {'pagenum': '3', 'signx': '0.1', 'signy': '0.1'}
            ...
        ]
        
        auto_complete : if "1", the document will be completed when all signatories
                        signed off; if "0", you can add new signatories even all
                        other signatories signed off, and you need end the document
                        yourself.
        seal_name : specify the seal used in this signing.
        notice_url : A POST url which will get the sign status when signed off.

        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'AutoSignFopp.json'
        path = '/open/' + method
        
        content = {
            'signid': sign_id,
            'email': user_account,
            'Coordinatelist': sign_positions,
            'openflag': auto_complete
        }
        if seal_name:
            content['sealname'] = seal_name
        if notice_url:
            content['noticeUrls'] = notice_url
        
        return self.post_request(method, path, content)
    
    def get_sign_page_link(self, sign_id, user_account, sign_positions,
                           return_url, page_type, push_url=None):
        """
        Get specified sign page link for a signatory.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
        user_account : a mobile or an email.
        sign_positions : a list contains sign positions.
        
        [
            {'pagenum': '1', 'signx': '0.5', 'signy': '0.5'},
            {'pagenum': '3', 'signx': '0.1', 'signy': '0.1'}
            ...
        ]
        
        return_url : will return to this URL after signing off.
        page_type : web page type. "1" is fit for PC; "2" is fit for mobile devices.
        push_url : BestSign server will send message to this URL after signing off.
                  
        Returns
        -------
        A URL for user to sign document on Web.
        """
        method = 'getSignPageSignimagePc.json'
        path = '/openpagepp/' + method
        
        sign_data = get_sign_data(method, self.mid, sign_id, user_account,
                                  sign_positions, return_url, page_type)
        content = {
            'mid': self.mid,
            'sign': get_rsa_sign(sign_data, self.private_key),
            'fsid': sign_id,
            'Coordinatelist': sign_positions,
            'typedevice': page_type,
            'email': user_account,
            'returnurl': return_url
        }
        if push_url:
            content['Pushurl'] = push_url
            
        self.logger.info("API path: [{0}]".format(path))
        self.logger.debug("Sign page parameters: \n[{0}]".format(content))
        
        link_param = urllib.parse.urlencode(content)
        return self.url + path + '?' + link_param
        
    def end_document(self, sign_id):
        """
        End document signing.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
                  
        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'endcontract.json'
        path = '/open/' + method
        
        content = {
            'signid': sign_id
        }
        
        return self.post_request(method, path, content)
    
    def query_user_documents(self, status, user_account='', start_time='',
                             end_time=''):
        """
        End documents about a user.
        
        Parameters
        ----------
        user_account : a mobile or an email.
        status : 1, need me to complete.
                 2, wait for others to complete.
                 3, completed.
                 4, canceled.
                 7, all status.
        start_time : time string like yyyy-MM-dd HH:mm:ss.
        end_time : time string like yyyy-MM-dd HH:mm:ss.
                  
        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'contractQuerybyEmail.json'
        path = '/open/' + method
        
        content = {
            'email': user_account,
            'status': status,
            'starttime': start_time,
            'endtime': end_time
        }
        
        return self.post_request(method, path, content)
    
    def query_document(self, sign_id):
        """
        End document by sign id.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
                  
        Returns
        -------
        A JSON response from BestSign server.
        """
        method = 'contractInfo.json'
        path = '/open/' + method
        
        content = {
            'fsdid': sign_id
        }
        
        return self.post_request(method, path, content)
    
    def view_document(self, sign_id, doc_id):
        """
        Return an URL to view the document.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
        doc_id : file id represents for the document file. This id can be parsed
                 from response of send document.
                 
        Returns
        -------
        A URL to view the document on Web.
        """
        method = 'ViewContract.page'
        path = '/openpage/' + method
        
        sign_data = get_sign_data(method, self.mid, sign_id, doc_id)
        
        content = {
            'mid': self.mid,
            'sign': get_rsa_sign(sign_data, self.private_key),
            'fsdid': sign_id,
            'docid': doc_id
        }
        
        self.logger.info("API path: [{0}]".format(path))
        self.logger.debug("View document parameters: \n[{0}]".format(content))
        
        link_param = urllib.parse.urlencode(content)
        return self.url + path + '?' + link_param
    
    def get_download_document_url(self, sign_id, file_type='zip'):
        """
        Return an URL to download the document.
        
        Parameters
        ----------
        sign_id : document id represents for one mission of sign. This id can be
                  parsed from response of send document.
        file_type : can be "zip" or "pdf".
                 
        Returns
        -------
        A URL to download the document.
        """
        method = ''
        if file_type == 'zip':
            method = 'contractDownload.page'
        elif file_type == 'pdf':
            method = 'contractDownloadMobile.page'
        else:
            raise AssertionError("Do not support file type: [{0}]".format(file_type))
        
        path = "/openpage/" + method
        status = "3"
        
        sign_data = get_sign_data(method, self.mid, sign_id, status)
        
        content = {
            'mid': self.mid,
            'sign': get_rsa_sign(sign_data, self.private_key),
            'fsdid': sign_id,
            'status': status,
        }
        
        self.logger.info("API path: [{0}]".format(path))
        self.logger.debug("Download document parameters: \n[{0}]".format(content))
        
        link_param = urllib.parse.urlencode(content)
        return self.url + path + '?' + link_param
    
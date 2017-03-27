# -*- coding: utf-8 -*-

import re
import sys
from .base import AipBase
from .base import base64
from .base import json
from .base import urlencode
from .base import quote
from .base import Image
from .base import StringIO

class AipFace(AipBase):
    """
        Aip Face
    """

    __detectUrl = 'https://aip.baidubce.com/rest/2.0/face/v1/detect'

    __matchUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/match'

    __addUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/user/add'

    __updateUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/user/update'

    __deleteUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/user/delete'

    __verifyUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/verify'

    __identifyUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/identify'

    __getUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/user/get'

    __getGroupListUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/group/getlist'

    __getGroupUsersUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/group/getusers'

    __addGroupUserUrl = 'https://aip.baidubce.com/rest/2.0/faceverify/v1/faceset/group/adduser'

    __deleteGroupUserUrl = ('https://aip.baidubce.com'
                            '/rest/2.0/faceverify/v1/faceset/group/deleteuser')    


    def detect(self, image, options=None):
        """
            face attributes detect
        """

        options = options or {}
        data = {}
        data['image'] = image
        data['max_face_num'] = options.get('max_face_num', '1')
        data['face_fields'] = options.get('face_fields', '')

        return self._request(self.__detectUrl, data)

    def __getEncodeImages(self, images):
        """
            encode image array
        """

        if isinstance(images, bytes):
            return base64.b64encode(images)

        result = []
        
        for image in images:
            if image:
                result.append(base64.b64encode(image).decode())        

        return result

    def match(self, images):
        """
            match
        """

        data = {}
        data['images'] = images if isinstance(images, list) else [images]

        return self._request(self.__matchUrl, data)

    def _validate(self, url, data):
        """
            validate
        """

        # user_info参数 不超过256B
        if 'user_info' in data:
            if len(data['user_info']) > 256:
                return {
                    'error_code': 'SDK103',
                    'error_msg': 'user_info size error',
                }

        # group_id参数 组成为字母/数字/下划线，且不超过128B
        if 'group_id' in data:
            if not re.match(r'^\w+$', str(data['group_id'])):
                return {
                    'error_code': 'SDK104',
                    'error_msg': 'group_id format error',
                }
            if len(data['group_id']) > 128:
                return {
                    'error_code': 'SDK105',
                    'error_msg': 'group_id size error',
                }

        # uid参数 组成为字母/数字/下划线，且不超过128B
        if 'uid' in data:
            if not re.match(r'^\w+$', str(data['uid'])):
                return {
                    'error_code': 'SDK106',
                    'error_msg': 'uid format error',
                }
            if len(data['uid']) > 128:
                return {
                    'error_code': 'SDK107',
                    'error_msg': 'uid size error',
                }

        if 'image' in data:
            data['image'] = self.__getEncodeImages(data['image'])
            
            # 编码后小于2m
            if not data['image'] or len(data['image']) >= 2 * 1024 * 1024:
                return {
                    'error_code': 'SDK100',
                    'error_msg': 'image size error',
                }
        elif 'images' in data:
            images = self.__getEncodeImages(data['images'])
            data['images'] = ','.join(images)

            # 人脸比对 编码后小于20m 其他 10m
            maxlen = (20 if url == self.__matchUrl else 10) * 1024 * 1024
            maxcount = (2 if url == self.__matchUrl else 1) 
            if len(images) < maxcount or len(data['images']) >= maxlen:
                return {
                    'error_code': 'SDK100',
                    'error_msg': 'image size error',
                }

        return True

    def addUser(self, uid, userInfo, groupId, images):
        """
            addUser
        """

        data = {}
        data['uid'] = str(uid)
        data['user_info'] = str(userInfo)
        data['group_id'] = str(groupId)
        data['images'] = images if isinstance(images, list) else [images]

        return self._request(self.__addUserUrl, data)

    def updateUser(self, uid, images):
        """
            updateUser
        """

        data = {}
        data['uid'] = str(uid)
        data['images'] = images if isinstance(images, list) else [images]

        return self._request(self.__updateUserUrl, data)

    def deleteUser(self, uid):
        """
            deleteUser
        """

        data = {}
        data['uid'] = str(uid)

        return self._request(self.__deleteUserUrl, data)

    def verifyUser(self, uid, images, options=None):
        """
            verifyUser
        """

        options = options or {}
        data = {}
        data['uid'] = str(uid)
        data['images'] = images if isinstance(images, list) else [images]
        data['top_num'] = options.get('top_num', 1)

        return self._request(self.__verifyUserUrl, data)

    def identifyUser(self, groupId, images, options=None):
        """
            identifyUser
        """

        options = options or {}
        data = {}
        data['group_id'] = str(groupId)
        data['images'] = images if isinstance(images, list) else [images]
        data['user_top_num'] = options.get('user_top_num', 1)
        data['face_top_num'] = options.get('face_top_num', 1)

        return self._request(self.__identifyUserUrl, data)

    def getUser(self, uid):
        """
            getUser
        """

        data = {}
        data['uid'] = str(uid)

        return self._request(self.__getUserUrl, data)

    def getGroupList(self, options=None):
        """
            getGroupList
        """

        options = options or {}
        data = {}
        data['start'] = options.get('start', 0)
        data['num'] = options.get('num', 100)

        return self._request(self.__getGroupListUrl, data)

    def getGroupUsers(self, groupId, options=None):
        """
            getGroupUsers
        """

        options = options or {}
        data = {}
        data['group_id'] = str(groupId)
        data['start'] = options.get('start', 0)
        data['num'] = options.get('num', 100)

        return self._request(self.__getGroupUsersUrl, data)

    def addGroupUser(self, groupId, uid):
        """
            addGroupUser
        """

        data = {}
        data['uid'] = str(uid)
        data['group_id'] = str(groupId)

        return self._request(self.__addGroupUserUrl, data)

    def deleteGroupUser(self, groupId, uid):
        """
            deleteGroupUser
        """

        data = {}
        data['uid'] = str(uid)
        data['group_id'] = str(groupId)

        return self._request(self.__deleteUserUrl, data)


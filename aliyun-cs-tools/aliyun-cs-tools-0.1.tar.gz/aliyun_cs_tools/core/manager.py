#!/usr/bin/env python2
# coding=utf-8
import json
import os
import requests

from aliyunsdkcs.request.v20151215 import DescribeClusterDetailRequest, DescribeClusterCertsRequest
from aliyunsdkcore.client import AcsClient

# req = DescribeClusterDetailRequest.DescribeClusterDetailRequest()
# req.set_ClusterId('c911e253d13d242db824516e16a5d80d2')
# client = AcsClient('LTAIhau268vgdGrY', 'D9BflMzKgwrbKRMi7vCT3CxxzSPDnm', 'cn-beijing')
#
# status, headers, body = client.get_response(req)
# master_url = json.loads(body).get('master_url')
# print(master_url)

# req = DescribeClusterCertsRequest.DescribeClusterCertsRequest()
# req.set_ClusterId('c911e253d13d242db824516e16a5d80d2')
# status, headers, body = client.get_response(req)
# print(body)


class AliCSManager(object):
    def __init__(self, ak, secret, region, cluster_id):
        self.cluster_id = cluster_id
        self.client = AcsClient(ak, secret, region)
        self.master_url = self.get_master_url()
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', self.cluster_id)
        self.ca_file_path = os.path.join(self.cache_dir, 'ca.pem')
        self.cert_file_path = os.path.join(self.cache_dir, 'cert.pem')
        self.key_file_path = os.path.join(self.cache_dir, 'key.pem')


    def get_master_url(self):
        master_url = None
        req = DescribeClusterDetailRequest.DescribeClusterDetailRequest()
        req.set_ClusterId(self.cluster_id)
        status, headers, body = self.client.get_response(req)
        if status == 200:
            master_url = json.loads(body).get('master_url')
        return master_url

    def update_cert(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        req = DescribeClusterCertsRequest.DescribeClusterCertsRequest()
        req.set_ClusterId(self.cluster_id)
        status, headers, body = self.client.get_response(req)
        if status == 200:
            data = json.loads(body)
            ca_string = data.get('ca')
            cert_string = data.get('cert')
            key_string = data.get('key')
            with open(self.ca_file_path, 'w') as f:
                f.write(ca_string)
            with open(self.cert_file_path, 'w') as f:
                f.write(cert_string)
            with open(self.key_file_path, 'w') as f:
                f.write(key_string)
        return True

    def _version_auto_increment(self, version):
        """
        实现version的子版本号的自增
        :param version:
        :return:
        """
        _v = version.split('.')
        try:
            _v[-1] = str(int(_v[-1]) + 1)
        except ValueError:
            _v[-1] = "%s.%s" % (_v[-1], '1')
        return '.'.join(_v)

    def get_project_info(self, name):
        url = "%s/projects/%s" % (self.master_url, name)
        resp = requests.get(
            url=url,
            verify=self.ca_file_path,
            cert=(self.cert_file_path,self.key_file_path)
        )
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data

    def update_project_config(self, name, version=None, environment=None, description=None):
        """

        :param name: 应用名
        :param version:  更新的应用版本，如果为空，默认子版本号自增1
        :param environment: 更新的应用描述。为一个字典，environment中没有指定的变量，会继续使用老版本中的值
        :param description: key/value 用于替换 Compose 模板的环境变量
        :return:

        """
        project_info = self.get_project_info(name)

        if not project_info:
            return False, 'get project info failed'

        new_environment = project_info.get('environment')
        if isinstance(environment, dict):
            new_environment.update(environment)

        if not version:
            version = self._version_auto_increment(project_info.get('version'))
        body ={
            'version': version,
            'template': project_info.get('template'),
            'environment': new_environment,
        }

        if description:
            body.update({'description': description})

        url = "%s/projects/%s/update" % (self.master_url, name)
        resp = requests.post(
            url=url,
            verify=self.ca_file_path,
            cert=(self.cert_file_path, self.key_file_path),
            json=body,
            headers={'Content-Type': 'application/json'},
        )
        if resp.status_code == 202:
            return True, 'success'
        return False, resp.text

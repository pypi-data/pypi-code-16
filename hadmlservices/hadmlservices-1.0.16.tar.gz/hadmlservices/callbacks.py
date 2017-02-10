"""
Provides methods to communicate with HAD ML Services (HMLS).
"""
import boto3
import json
import urllib
import botocore
import os


class CB(object):

    def __init__(self):
        # TODO handle cases: 
        # 1. runs on not aws instance
        # 2. runs outside of Service environment
        self.lbd = boto3.client('lambda', region_name='us-east-1')
        #self.ec2 = boto3.client('ec2', region_name='us-east-1')
        url = "http://169.254.169.254/latest/meta-data/instance-id"
        self.instance_id = urllib.urlopen(url).read()

    def update_job(self, key, value):
        #try:
        json_params = {
            'instance_id': self.instance_id,
             key: value
        }
        lambda_fun = "had-rds-update"
        if os.environ.get('HADMLSERVICE_PROD')== '1':
            lambda_fun +=':prod'
        self.lbd.invoke(
            FunctionName=lambda_fun,
            InvocationType='Event',
            Payload=json.dumps(json_params)
        )
        """
        except botocore.exceptions.NoCredentialsError as e:
            print("NoCredentialsError: {}".format(e))
            print("Most likely running outside of HAD API Service environment.")
            return
        except botocore.exceptions.ClientError as e:
            print "ClientError: {}".format(e)
            raise
        """

    def terminate_instance(self):
        json_params = {
            'instance_id': self.instance_id
        }
        lambda_fun = "had-ec2-terminate"
        self.lbd.invoke(
            FunctionName=lambda_fun,
            InvocationType='Event',
            Payload=json.dumps(json_params)
        )     


"""
Provides methods to communicate with HAD ML Services (HMLS).
"""
import boto3
import json
import urllib
import botocore
import os
import time


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
        for i in range (0,5):
            try:
	        self.lbd.invoke(
                        FunctionName=lambda_fun,
                        InvocationType='Event',
                        Payload=json.dumps(json_params)
                )
	    except botocore.exceptions.EndpointConnectionError as e:
                print "Attempt {} out of 5 to connect to Lambda service".format(i)
                print e
                time.sleep(3)
                continue
            break
               
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
        for i in range (0,5):
            try:
                self.lbd.invoke(
                        FunctionName=lambda_fun,
                        InvocationType='Event',
                        Payload=json.dumps(json_params)
                )
            except botocore.exceptions.EndpointConnectionError as e:
                print "Attempt {} out of 5 to connect to Lambda service".format(i)
                print e
                time.sleep(3)
                continue
            break


# -*- coding: utf-8 -*-

import os
import boto3
import sys


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


def init(bucket, path, region):
    client = boto3.client('s3')
    try:
        if region != 'us-east-1':
            client.create_bucket(Bucket=bucket, ACL='private',
                                 CreateBucketConfiguration={'LocationConstraint': region})
        else:
            client.create_bucket(Bucket=bucket, ACL='private')
    except Exception as e:
        print(repr(e))
        sys.exit(1)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print('INFO: Uploading ')
    for root, dirs, files in os.walk(os.path.join(dir_path, 'config-templates')):
        for file in files:
            s3key = os.path.join(path, '/'.join(dirs), file)
            try:
                client.head_object(Bucket=bucket, Key=s3key)
            except:
                client.upload_file(os.path.join(root, file),
                                   bucket, s3key)

    print('INFO: Succesfuly initialized in {} with store {}/{}'.format(region, bucket, path))

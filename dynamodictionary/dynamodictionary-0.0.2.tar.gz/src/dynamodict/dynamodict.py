#!/usr/bin/python
"""a class that acts a little like a dictionary that uses dynamo as a backing"""
# std imports
import base64
import sys
import time

# site imports
import boto3
import botocore.exceptions
import cbor2

# user imports


def serialize(obj):
    return base64.b64encode(cbor2.dumps(obj))


def deserialize(obj):
    return cbor2.loads(base64.b64decode(obj))


class DynamoDictionary(object):
    """a class that acts a little like a dictionary that uses dynamo as a backing"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.conn = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.conn.Table(self.table_name)
        try:
            self.table.get_item(Key={'key': "test"})
        except botocore.exceptions.ClientError:
            print >> sys.stderr, "Table did not exist, making it now!"
            self.create_table()
            print >> sys.stderr, "Waiting for table to be ready to query!"
            self.table.wait_until_exists()

    def create_table(self):
        self.client.create_table(
            TableName=self.table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

    def __getitem__(self, key):
        got = self.table.get_item(Key={'key': serialize(key)})
        if 'Item' not in got:
            raise KeyError(key)
        return deserialize(got['Item']['value'])

    def __setitem__(self, key, value):
        skey = serialize(key)
        sval = serialize(value)
        for i in xrange(5):
            try:
                self.table.put_item(Item={'key': skey, 'value': sval})
                break
            except botocore.exceptions.ClientError as oops:
                if oops.response['Error'][
                        'Code'] != 'ProvisionedThroughputExceededException':
                    raise
                else:
                    print >> sys.stderr, "Over rate limit, backing off!"
                    time.sleep(0.1 * 2**i)
        else:
            raise Exception("Tried 5 times could not write item!")

    def get(self, key, default=None):
        try:
            return self.__getitem__(serialize(key))
        except KeyError:
            return default

    def pop(self, key, default=None):
        deleted = self.table.delete_item(
            Key={'key': serialize(key)}, ReturnValues='ALL_OLD')
        if 'Attributes' not in deleted:
            return default
        return deleted['Attributes']['value']

    def iteritems(self):
        start_key = ""
        while True:
            kwargs = {
                "Limit": 1000,
                "Select": 'ALL_ATTRIBUTES',
            }
            if start_key:
                kwargs['ExclusiveStartKey'] = start_key
            response = self.table.scan(
                **kwargs
            )
            for item in response['Items']:
                yield deserialize(item['key']), deserialize(item['value'])
            start_key = response.get("LastEvaluatedKey")
            if start_key is None:
                break

    def __iter__(self):
        for key, _ in self.iteritems():
            yield key

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

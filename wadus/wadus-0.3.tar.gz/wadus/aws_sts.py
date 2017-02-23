import boto3

class AwsSts:
    def __init__(self):
        self.sts = boto3.client('sts')

    def get_info(self):
        return self.sts.get_caller_identity()

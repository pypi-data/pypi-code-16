import boto3
from terminaltables import AsciiTable
from wadus.aws_sts import AwsSts

class AwsAmis:
    def __init__(self):
        self.ec2 = boto3.client('ec2')

    def list(self):
        aws_sts = AwsSts()
        sts_info = aws_sts.get_info()
        amis_info = self.ec2.describe_images(Filters=[{'Name':'owner-id', 'Values':[sts_info.get('Account')]}])
        self.print_table(amis_info.get('Images'))

    def print_table(self, images):
        table_data = [['AMI ID', 'Creation date', 'AMI Name']]
        for i in images:
            table_data.append([i.get('ImageId'),
                               i.get('CreationDate'),
                               i.get('Name')])
        table = AsciiTable(table_data)
        print(table.table)

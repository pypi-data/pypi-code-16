import boto3
from terminaltables import AsciiTable

class AwsInstances:
    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def list(self):
        filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
        instances = self.ec2.instances.filter(Filters=filters)
        self.print_table(instances)

    def print_table(self, instances):
        table_data = [['Name', 'ID', 'Type', 'Public IP', 'Private IP', 'Zone', 'Roles', 'Stages']]
        for i in instances:
            if i.tags:
                tags = dict(map((lambda x: [x['Key'],x['Value']]),i.tags))
                table_data.append([tags.get('Name'),
                                  i.id,
                                  i.instance_type,
                                  i.public_ip_address,
                                  i.private_ip_address,
                                  i.placement['AvailabilityZone'],
                                  tags.get('Roles'),
                                  tags.get('Stages')])
        table = AsciiTable(table_data)
        print(table.table)

import boto3
from terminaltables import AsciiTable

class AwsBalancers:
    def __init__(self):
        self.elb = boto3.client('elb')

    def list(self):
        balancers_info = self.elb.describe_load_balancers()
        self.print_table(balancers_info.get('LoadBalancerDescriptions'))

    def print_table(self, balancers):
        table_data = [['Name', 'DNS', 'Instances', 'Availability Zones']]
        for b in balancers:
            table_data.append([b.get('LoadBalancerName'),
                               b.get('DNSName'),
                               len(b.get('Instances')),
                               ', '.join(b.get('AvailabilityZones'))])
        table = AsciiTable(table_data)
        print(table.table)

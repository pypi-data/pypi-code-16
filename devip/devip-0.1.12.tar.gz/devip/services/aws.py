import boto3

from devip.service import Service


class AmazonWebService(Service):
    name = 'aws'
    default_settings = {
        'profile': 'default',
        'security_group': None
    }
    required_settings = ['security_group']

    def __init__(self):
        super(AmazonWebService, self).__init__()
        self.client = boto3.Session(profile_name=self.profile).client('ec2')

    @staticmethod
    def _create_ip_permissions(ip):
        return {
            'ToPort': 65535,
            'FromPort': 0,
            'IpRanges': [{'CidrIp': ip}],
            'IpProtocol': 'tcp'
        }

    def get_service_ips(self):
        group = self.client.describe_security_groups(GroupIds=[self.security_group])['SecurityGroups'][0]
        return [x['CidrIp'] for x in group['IpPermissions'][0]['IpRanges']]

    def allow_ip(self, ip):
        self.client.authorize_security_group_ingress(
            GroupId=self.security_group,
            IpPermissions=[AmazonWebService._create_ip_permissions(ip)]
        )

    def revoke_ip(self, ip):
        self.client.revoke_security_group_ingress(
            GroupId=self.security_group,
            IpPermissions=[AmazonWebService._create_ip_permissions(ip)]
        )

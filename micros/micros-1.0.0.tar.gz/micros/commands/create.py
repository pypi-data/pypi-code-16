"""The create command."""

from .base import Base

import boto3
import uuid
import json

# Specify the region to create the AWS resources in
DEFAULT_REGION = "eu-west-1"

# A mapping of hosted zone IDs to AWS regions.
# Apparently this data is not accessible via API
# http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
# https://forums.aws.amazon.com/thread.jspa?threadID=116724
S3_HOSTED_ZONE_IDS = {
    'us-east-1': 'Z3AQBSTGFYJSTF',
    'us-west-1': 'Z2F56UZL2M1ACD',
    'us-west-2': 'Z3BJ6K6RIION7M',
    'ap-south-1': 'Z11RGJOFQNVJUP',
    'ap-northeast-1': 'Z2M4EHUR26P7ZW',
    'ap-northeast-2': 'Z3W03O7B5YMIYP',
    'ap-southeast-1': 'Z3O0J2DXBE1FTB',
    'ap-southeast-2': 'Z1WCIGYICN2BYD',
    'eu-central-1': 'Z21DNDUVLTQW6Q',
    'eu-west-1': 'Z1BKCTXD74EZPE',
    'sa-east-1': 'Z7KQH4QJS55SO',
    'us-gov-west-1': 'Z31GFT0UA1I2HV',
}


class Create(Base):

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def run(self):
        """Create static site environment"""
        project_name = self.options['<project>']
        create_redirect_bucket = self.options['--create_www']
        create_hosted_zone = self.options['--create_zone']

        self.create_main_bucket(project_name)
        self.create_www_bucket(project_name) if create_redirect_bucket else print('--create_www flag not given')
        self.create_route53_zone(project_name) if create_hosted_zone else print('--create_www flag not given')

    @staticmethod
    def create_main_bucket(project_name):
        s3 = boto3.resource('s3')

        try:

            # Create a new S3 bucket, using a demo bucket name
            s3.create_bucket(
                Bucket=project_name,
                CreateBucketConfiguration={
                    'LocationConstraint': 'eu-west-1'
                },
             )

            # We need to set an S3 policy for our bucket to
            # allow anyone read access to our bucket and files.
            # If we do not set this policy, people will not be
            # able to view our S3 static web site.
            bucket_policy = s3.BucketPolicy(project_name)
            policy_payload = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "Allow Public Access to All Objects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::%s/*" % project_name
                }
                ]
            }

            # Add the policy to the bucket
            bucket_policy.put(Policy=json.dumps(policy_payload))

            # Next we'll set a basic configuration for the static
            # website.
            website_payload = {
                'ErrorDocument': {
                    'Key': 'error.html'
                },
                'IndexDocument': {
                    'Suffix': 'index.html'
                }
            }

            # Make our new S3 bucket a static website
            bucket_website = s3.BucketWebsite(project_name)

            # And configure the static website with our desired index.html
            # and error.html configuration.
            bucket_website.put(WebsiteConfiguration=website_payload)
            print('Static website created successfully, use the deploy function to write files to the new environment. '
                  'Visit http://{0}.s3-website-eu-west-1.amazonaws.com to view your website'.format(project_name))

        except Exception as e:
            if 'BucketAlreadyExists' in str(e):
                print('ERROR(1000): BucketAlreadyExists - '
                      'The requested bucket name is not available. Please select a different name and try again.')
                exit(1)
            elif 'BucketAlreadyOwnedByYou' in str(e):
                print('ERROR(1001): BucketAlreadyOwnedByYou: - '
                      'our previous request to create the named bucket succeeded and/or you already own it.')
                exit(1)

    @staticmethod
    def create_www_bucket(project_name):

        # Create S3 resource
        s3 = boto3.resource('s3')

        try:
            # Create a new S3 bucket, using the www demo bucket name
            redirect_bucket_name = "www." + project_name

            s3.create_bucket(
                Bucket=redirect_bucket_name,
                CreateBucketConfiguration={
                     'LocationConstraint': 'eu-west-1'
                },
            )

            # The S3 settings to redirect to the root domain,
            # in this case the bucket_name variable from above.
            redirect_payload = {
                'RedirectAllRequestsTo': {
                    'HostName': '%s' % project_name,
                    'Protocol': 'http'
                }
            }

            # Make our redirect bucket a S3 website
            bucket_website_redirect = s3.BucketWebsite(redirect_bucket_name)

            # Set the new bucket to redirect to our root domain
            # with the redirect payload above.
            bucket_website_redirect.put(WebsiteConfiguration=redirect_payload)

        except Exception as e:
            if 'BucketAlreadyExists' in str(e):
                print('ERROR(1000): BucketAlreadyExists - '
                      'The requested bucket name is not available. Please select a different name and try again.')
                exit(1)
            elif 'BucketAlreadyOwnedByYou' in str(e):
                print('ERROR(1001): BucketAlreadyOwnedByYou: - '
                      'our previous request to create the named bucket succeeded and/or you already own it.')
                exit(1)

    @staticmethod
    def create_route53_zone(project_name):

        # Load Route53 module
        route53 = boto3.client('route53')

        # Define the domain name we want to add in Route53
        www_redirect = "www." + project_name

        # We need to create a unique string to identify the request.
        # A UUID4 string is an easy to use unique identifier.
        caller_reference_uuid = "%s" % (uuid.uuid4())

        # Create the new hosted zone in Route53
        response = route53.create_hosted_zone(
            Name=project_name,
            CallerReference=caller_reference_uuid,
            HostedZoneConfig={'Comment': project_name, 'PrivateZone': False})

        # Get the newly created hosted zone id, used for
        # adding our DNS records pointing to our S3 buckets
        hosted_zone_id = response['HostedZone']['Id']

        # Add DNS records for domain.com and www.domain.com
        website_dns_name = "s3-website-%s.amazonaws.com" % DEFAULT_REGION
        redirect_dns_name = "s3-website-%s.amazonaws.com" % DEFAULT_REGION

        # Here is the payload we will send to Route53
        # We are creating two DNS records:
        # one for domain.com to point to our S3 bucket,
        # and a second for www.domain.com to point to our
        # S3 redirect bucket, to redirect to domain.com
        change_batch_payload = {
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': project_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': S3_HOSTED_ZONE_IDS[DEFAULT_REGION],
                            'DNSName': website_dns_name,
                            'EvaluateTargetHealth': False
                        }
                    }
                },
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': www_redirect,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': S3_HOSTED_ZONE_IDS[DEFAULT_REGION],
                            'DNSName': redirect_dns_name,
                            'EvaluateTargetHealth': False
                        }
                    }
                }
            ]
        }

        # Create the DNS records payload in Route53
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch_payload)
        print(response)

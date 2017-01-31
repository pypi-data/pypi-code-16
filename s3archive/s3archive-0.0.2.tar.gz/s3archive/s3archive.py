import os
import re
import csv
import boto3

class Archive:
    CSV_DELIMITER = ','
    S3_RESOURCE = 's3'
    S3_VERSION = 's3v4'

    def __init__(self, bucket, csv_keys):
        # Take the S3 bucket.
        with open(os.path.expanduser(csv_keys), 'r') as csv_file:
            s3_config = csv.reader(csv_file, delimiter=Archive.CSV_DELIMITER)
            # Skip headers in the Amazon csv.
            next(s3_config)
            s3_key, s3_secret = next(s3_config)
            s3_resource = boto3.resource(
                Archive.S3_RESOURCE,
                config=boto3.session.Config(signature_version=Archive.S3_VERSION),
                aws_access_key_id=s3_key,
                aws_secret_access_key=s3_secret,
            )
            self.bucket = s3_resource.Bucket(bucket)

    def find(self, regex):
        """Returns a generator of s3 objects that match the given regex in the form of (key, file_object)."""
        return ((f.key, f.get()['Body']) for f in self.bucket.objects.all() if re.match(regex, f.key))

    def exists(self, regex):
        """Returns False if there are no matches for the given regex."""
        return bool(next(self.find(regex), None))

    def upload(self, source, destination):
        """Uploads a file from the given source to the given destination on S3."""
        self.upload_file(open(source, 'rb'), destination)

    def upload_file(self, file_object, destination):
        """Uploads a file to S3 with the given destination."""
        self.bucket.put_object(
            Key=destination,
            Body=file_object,
        )

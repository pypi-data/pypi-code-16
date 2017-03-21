"""The delete command."""

from __future__ import absolute_import, division, print_function

from .base import Base
import boto3


class Delete(Base):

    def run(self):
        """Deletes the S3 bucket project by destroying the bucket"""
        s3 = boto3.resource('s3')
        project_name = self.options['<project>']
        try:
            bucket = s3.Bucket(project_name)
            for obj in bucket.objects.filter(Prefix=''):
                s3.Object(bucket.name, obj.key).delete()
            bucket.delete()
            print('static site destroyed, and project is deleted.')
        except Exception as e:
            print(e)

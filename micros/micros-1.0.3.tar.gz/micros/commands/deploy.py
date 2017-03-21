"""The deploy command."""

from __future__ import absolute_import, division, print_function

from .base import Base

import os
import boto3
import mimetypes


class Deploy(Base):

    def run(self):
        """Deploy static site from Github to AWS S3"""
        s3 = boto3.resource('s3')

        project_name = self.options['<project>']
        local_directory = self.options['<directory>']
        bucket = project_name
        mimetypes.init()

        for root, dirs, files in os.walk(local_directory):

            for filename in files:

                local_path = os.path.join(root, filename)
                fbytes = open(local_path, 'rb')

                # guess the extension and
                file_type = mimetypes.types_map['.' + filename.rsplit('.', 1)[1]]
                s3.Object(bucket, filename).put(Body=fbytes, ContentType=file_type)

                print('Uploading {0}'.format(filename))

        print('Deployment successful. visit http://{0}.s3-website-eu-west-1.amazonaws.com'.format(project_name))

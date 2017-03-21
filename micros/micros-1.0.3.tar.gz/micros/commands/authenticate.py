"""The authenticate command."""

from __future__ import absolute_import, division, print_function

import os.path
import platform
from .base import Base


class Authenticate(Base):
    """Authenticate to AWS"""

    def run(self):
        file_path = self.options['<aws-folder>']
        aws_id = self.options['<aws_key>']
        aws_secret = self.options['<aws_secret>']

        try:
            print('creating AWS auth config location')
            if 'Windows' in platform.system():
                os.makedirs(file_path, exist_ok=True)
                auth_file = open(file_path + 'credentials', 'w')
            else:
                os.makedirs(file_path, exist_ok=True)
                auth_file = open(file_path + 'credentials', 'w')

            auth_file.write('[default]\n')
            auth_file.write('aws_access_key_id = {0}\n'.format(aws_id))
            auth_file.write('aws_secret_access_key = {0}\n'.format(aws_secret))

        except Exception as e:
            print(e)

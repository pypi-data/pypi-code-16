"""The authenticate command."""

from __future__ import absolute_import, division, print_function

import os.path
from .base import Base


class Authenticate(Base):
    """Authenticate to AWS"""

    def run(self):
        file_path = self.options['<cred-file>']
        aws_id = self.options['<aws_key>']
        aws_secret = self.options['<aws_secret>']

        if not os.path.exists(file_path):
            auth_file = open(file_path, 'w')
            auth_file.write('[default]\n')
            auth_file.write('aws_access_key_id = {0}\n'.format(aws_id))
            auth_file.write('aws_secret_access_key = {0}\n'.format(aws_secret))
        else:
            print('ERROR(1002): Auth file already exists, please check {0}'.format(file_path))

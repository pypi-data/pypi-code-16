from serapeum.backup.modules.log import logger

from serapeum.backup.modules.rdiff import RdiffRole


##
# TODO
# Make destination OK
# Use configuration file OK
# Implement delete-older-than OK
# Logger OK


class Files:

    def __init__(self, remote_role, sources_file, destination_path, remote_user, remote_host, ssh_key,
                 excludes_file=None, delete_older_than=None):
        self.remote_role = remote_role
        self.remote_host = remote_host
        self.remote = self.remote_host
        self.destination_path = destination_path
        self.rdiff = RdiffRole(remote_role=remote_role, sources=sources_file, destination_path=destination_path,
                               remote_user=remote_user, remote_host=remote_host, ssh_key=ssh_key,
                               excludes=excludes_file, delete_older_than=delete_older_than, sources_is_file=True,
                               excludes_is_file=True)
        self.cmd_output = ''

    def run(self):
        if self.remote_role == 'backup':
            logger.info('Performing backup to {0}::{1}.'.format(self.remote_host, self.destination_path))
        elif self.remote_role == 'source':
            logger.info('Performing backup of {0} to {1}.'.format(self.remote_host, self.destination_path))
        try:
            self.rdiff.run()
        except Exception as e:
            self.cmd_output = self.rdiff.cmd_output
            raise e
        self.cmd_output = self.rdiff.cmd_output
        return True

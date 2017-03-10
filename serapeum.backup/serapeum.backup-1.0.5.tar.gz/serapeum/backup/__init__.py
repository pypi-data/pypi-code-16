from os.path import abspath, dirname, join, isfile

from serapeum.backup.modules.config import Config
from serapeum.backup.modules.log import logger

if isfile('/etc/serapeum/backup.ini'):
    config = Config('/etc/serapeum/backup.ini')
else:
    config = Config(abspath(join(dirname(abspath(__file__)), '..', 'config', 'config.ini')))

from serapeum.backup.modules.ds.stack import Stack
from serapeum.backup.modules.files import Files
from serapeum.backup.modules.mysql import MySQLBackup
from serapeum.backup.modules.mail import Mail
from serapeum.backup.modules.remotes import Remotes


def job_queue():
    jobs = Stack()
    if config.config['BACKUP'].get('remote_loc'):
        jobs.add(Files(remote_role=config.config['BACKUP']['remote_role'],
                       sources_file=config.config['BACKUP']['sources_file'],
                       destination_path=config.config['BACKUP']['backup_path'],
                       remote_user=config.config['BACKUP']['remote_user'],
                       remote_host=config.config['BACKUP']['remote_loc'],
                       ssh_key=config.config['BACKUP']['remote_ssh'],
                       excludes_file=config.config['BACKUP']['excludes_file'],
                       delete_older_than=None))
    elif config.config['BACKUP'].get('remote_list'):
        for remote in Remotes(config.config['BACKUP'].get('remote_list')).remotes:
            if config.config['BACKUP']['remote_role'] == 'source':
                destination_path = '{0}/{1}'.format(config.config['BACKUP']['backup_path'], remote)
                jobs.add(Files(remote_role=config.config['BACKUP']['remote_role'],
                               sources_file=config.config['BACKUP']['sources_file'],
                               destination_path=destination_path,
                               remote_user=config.config['BACKUP']['remote_user'],
                               remote_host=remote,
                               ssh_key=config.config['BACKUP']['remote_ssh'],
                               excludes_file=config.config['BACKUP']['excludes_file'],
                               delete_older_than=None))
            elif config.config['BACKUP']['remote_role'] == 'backup':
                jobs.add(Files(remote_role=config.config['BACKUP']['remote_role'],
                               sources_file=config.config['BACKUP']['sources_file'],
                               destination_path=config.config['BACKUP']['backup_path'],
                               remote_user=config.config['BACKUP']['remote_user'],
                               remote_host=remote,
                               ssh_key=config.config['BACKUP']['remote_ssh'],
                               excludes_file=config.config['BACKUP']['excludes_file'],
                               delete_older_than=None))
    if config.config['MYSQL'].getboolean('backup_mysql') is True:
        if config.config['MYSQL'].get('remote_loc'):
            jobs.add(
                MySQLBackup(local_path=config.config['MYSQL']['local_path'], server_host=config.config['MYSQL']['host'],
                            server_user=config.config['MYSQL']['username'],
                            server_password=config.config['MYSQL']['password'],
                            backup_destination_path=config.config['MYSQL']['backup_path'],
                            backup_remote_host=config.config['MYSQL']['remote_loc'],
                            backup_remote_user=config.config['MYSQL']['remote_user'],
                            backup_ssh=config.config['MYSQL']['remote_ssh']))
        elif config.config['MYSQL'].get('remote_list'):
            for remote in Remotes(config.config['MYSQL'].get('remote_list')).remotes:
                if config.config['BACKUP']['remote_role'] == 'source':
                    destination_path = '{0}/{1}'.format(config.config['MYSQL']['backup_path'], remote)
                    jobs.add(
                        MySQLBackup(local_path=config.config['MYSQL']['local_path'],
                                    server_host=config.config['MYSQL']['host'],
                                    server_user=config.config['MYSQL']['username'],
                                    server_password=config.config['MYSQL']['password'],
                                    backup_destination_path=destination_path,
                                    backup_remote_host=remote,
                                    backup_remote_user=config.config['MYSQL']['remote_user'],
                                    backup_ssh=config.config['MYSQL']['remote_ssh']))
                elif config.config['BACKUP']['remote_role'] == 'backup':
                    jobs.add(
                        MySQLBackup(local_path=config.config['MYSQL']['local_path'],
                                    server_host=config.config['MYSQL']['host'],
                                    server_user=config.config['MYSQL']['username'],
                                    server_password=config.config['MYSQL']['password'],
                                    backup_destination_path=config.config['MYSQL']['backup_path'],
                                    backup_remote_host=remote,
                                    backup_remote_user=config.config['MYSQL']['remote_user'],
                                    backup_ssh=config.config['MYSQL']['remote_ssh']))
    return jobs


def main():
    jobs = job_queue()
    failures = False
    while True:
        job = jobs.pop()
        if job is None:
            break
        try:
            job.run()
        # except Exception as e:
        #    print(job.cmd_output)
        #    raise e
        except Exception as e:
            m = Mail(server=config.config['MAIL']['smtp_server'], port=config.config['MAIL']['smtp_port'],
                     username=config.config['MAIL']['smtp_username'], password=config.config['MAIL']['smtp_password'])
            m.send(sender=config.config['MAIL']['smtp_username'], recipient=config.config['MAIL']['mail_dest'],
                   msg_text="{0}\n{1}".format(job.cmd_output, e), subject='The backup job for {0} ({1}) failed.'
                   .format(job.remote, str(job)))
            logger.exception(job.cmd_output)
            failures = True
    if failures is True:
        return False
    return True

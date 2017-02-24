# coding: utf-8

import sys
import time
import click
import ConfigParser
import simplejson as json
from jinja2 import Template
import deployv
from deployv.base import commandv
from deployv.helpers import utils, build_helper
from deployv.instance import instancev
import os
import re

logger = utils.setup_deployv_logger('deployv')  # pylint: disable=C0103


@click.group()
def cli():
    logger.info('Deployv version: %s', deployv.__version__)


@cli.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
@click.option("-z", "--backup_dir", help="Directory where are the backups stored",
              default=False, required=True)
@click.option("-e", "--external", help=("Use external branches json file"
                                        " (generated with branchesv)"),
              default=False, required=False)
@click.option("-k", "--key_file", help="the key file to be used",
              default=False, required=False)
@click.option("--without-db", is_flag=True, default=False,
              help="If true, no database will be loaded inside the container. Default False")
@click.option("-d", "--database", help="Database name to be used",
              default=False, required=False)
@click.option("--without-demo", is_flag=True, default=False,
              help="If true, no database will be loaded demo data"
                   " inside the container. Default False")
def create(config_file, log_level, backup_dir, external, key_file, without_db, database,
           without_demo):
    """ Creates an instance then loads a backup from backup_dir folder
    """
    logger.setLevel(log_level)
    if external and not utils.validate_external_file(external):
        sys.exit(1)
    if key_file and not utils.validate_external_file(key_file):
        sys.exit(1)
    config = utils.merge_config(
        config_file, keys_file=key_file, branches=external)
    config = json.loads(Template(json.dumps(config)).render(config))
    config.get("container_config").get("env_vars").update({"without_demo": without_demo})
    if database:
        config.get("instance").get("config").update({"db_name": database})
    command = commandv.CommandV(config)
    res_create = command.create()
    if not res_create.get('result'):
        logger.error('Could not create the instance, some error raised: %s',
                     res_create.get('error'))
        sys.exit(1)
    if without_db:
        sys.exit(0)
    time.sleep(10)
    res_restore = command.restore(backup_dir, database_name=database)
    if res_restore.get('result', False):
        logger.info('Done')
    else:
        logger.warn(
            'Could not restore any backup to the desired instance: %s',
            res_restore.get('error'))
        sys.exit(1)
    sys.exit(0)


@cli.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=False)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
@click.option("-z", "--backup_dir", help="Directory where are the backups will be stored",
              default=False, required=True)
@click.option("-e", "--external", help=("Use external branches json file"
                                        " (generated with branchesv)"),
              default=False, required=False)
@click.option("-r", "--reason", help="Reason why the backup is being generated (optional)",
              default=False, required=False)
@click.option("--tmp-dir", help="Temp dir to use (optional)",
              default=False, required=False)
@click.option("-c", "--cformat", help="Compression format to be used (tar.bz2 or tar.gz)",
              default=False, required=False)
@click.option("-d", "--database", help="Database name",
              default=False, required=True)
@click.option("-n", "--container", help="Container name or id",
              default=False, required=False)
@click.option("-x", "--prefix", required=False,
              help="Prefix used for the database name and the backup database_name")
def backupdb(config_file, log_level, backup_dir,
             external, reason, tmp_dir, database, cformat, container, prefix):
    """ Generates a backup and saves it in backup_dir folder
    """
    logger.setLevel(log_level)
    if config_file and container:
        logger.error(
            'You cannot use both parameters, -n and -f. Use one or another')
        sys.exit(1)
    elif not config_file and not container:
        logger.error(
            'You must use one of the -z or -k parameters.')
        sys.exit(1)
    if config_file:
        if external and not utils.validate_external_file(external):
            sys.exit(1)
        config = utils.merge_config(config_file, branches=external)
        config = json.loads(Template(json.dumps(config)).render(config))
    elif container:
        config = {  # pylint: disable=R0204
            'container_config': {'container_name': container}
        }
    command = commandv.CommandV(config)
    res = command.backup(backup_dir, database, cformat, reason, tmp_dir, prefix)
    if res.get('result', False):
        logger.info('Backup generated: %s', res.get('result'))
        logger.info('Done')
    else:
        logger.error('Could not generate the backup: %s', res.get('error'))


@cli.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
@click.option("-z", "--backup_dir", help="Directory where are the backups are stored",
              default=False, required=True)
@click.option("-o", "--backup_file", help="Backup file to be restored",
              default=False, required=True)
@click.option("-d", "--database", help="Database name to be used",
              default=False, required=False)
@click.option("-n", "--container", help="Container name or id",
              default=False, required=False)
@click.option("-s", "--admin_pass", help="Admin password",
              default=False, required=False)
@click.option("-t", "--instance-type", type=click.Choice(instancev.INSTANCE_TYPES),
              help=("Specifies the type of instance. test, "
                    "develop, updates or production"))
@click.option("-x", "--prefix", required=False,
              help="Prefix used for the database name")
def restore(config_file, log_level, backup_dir, backup_file, database,
            container, admin_pass, instance_type, prefix):
    """ Restores a backup from a directory or a backup file
    """
    logger.setLevel(log_level)
    if config_file and container:
        logger.error(
            'You cannot use both parameters, -n and -f. Use one or another')
        sys.exit(1)
    elif not config_file and not container:
        logger.error(
            'You must use one of the -n or -f parameters.')
        sys.exit(1)
    if config_file:
        config = utils.merge_config(config_file)
        config = json.loads(Template(json.dumps(config)).render(config))
    if container:
        config = {  # pylint: disable=R0204
            'container_config': {'container_name': container},
            'instance': {'config': {'admin': admin_pass}}
        }
    if instance_type:
        config.get('instance').update({'instance_type': instance_type})
    if prefix:
        config.get('instance').update({'prefix': prefix.lower()})
    if backup_dir and backup_file:
        logger.error(
            'You cannot use both parameters, -z and -o. Use one or another')
        sys.exit(1)
    command = commandv.CommandV(config)
    if container and not prefix and not database:
        punctuation = '''!"#$%&'()*+,-.:;<=>?@[]^`{|}~'''
        dbfilter = command.instance_manager.docker_env.get('dbfilter', '')
        database = re.sub('[%s]' % re.escape(punctuation), '', dbfilter)
        if not database:
            logger.error(
                'Could not get the name of the database, '
                'please use the -x or -d parameter')
            sys.exit(1)
    if backup_dir:
        res = command.restore(backup_dir, database_name=database)
    elif backup_file:
        res = command.restore(backup_file, database_name=database)
    else:
        logger.error('You "must" use one of the -z or -o parameter')
        sys.exit(1)
    if res.get('result', False):
        message = "Backup {backup_name} restored in database {dbname}".\
            format(backup_name=res.get('result').get('backup'),
                   dbname=res.get('result').get('database_name'))
        logger.info(message)
        logger.info('Done')
    else:
        logger.error('Could not generate the backup: %s', res.get('error'))
        sys.exit(1)
    sys.exit(0)


@cli.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
@click.option("-d", "--database", help="Database name to be updated",
              default=False, required=False)
def update(config_file, log_level, database):
    """ Updates an existing instance, clone the branches to the specified ones and updates database
    """
    logger.setLevel(log_level)
    config = utils.load_json(config_file)
    config = json.loads(Template(json.dumps(config)).render(config))
    command = commandv.CommandV(config)
    res_create = command.create()
    if res_create.get('result', False):
        res_update = command.updatedb(database)
        if res_update.get('error', False):
            logger.error(
                'An error was detected during update process: %s', res_update.get('error'))
            sys.exit(1)
        else:
            logger.info('Update done')
            sys.exit(0)
    else:
        logger.error('the instance was not created: %s',
                     res_create.get('error'))
        sys.exit(1)


@cli.command()
@click.option("-n", "--container", help="Container name or id")
@click.option("-d", "--database", help="Database name to be used")
@click.option("-s", "--admin_password", help="Password used to log in as admin in odoo",
              required=False, default=False)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
def deactivate(container, database, log_level, admin_password):
    """ Deactivates a specific database inside a container.
    """
    logger.setLevel(log_level)
    config = {
        'container_config': {
            'container_name': container
        },
        'instance': {
            'config': {
                'admin': admin_password
            }
        }
    }
    command = commandv.CommandV(config)
    command.deactivate(database)


@cli.command()
@click.option("-x", "--prefix", required=True,
              help="Prefix used for the database name and the backup database_name")
@click.option("-l", "--log_level", help="Log level to show", default='INFO')
@click.option("-p", "--store_path", help="Directory where the deactivated backups will be stored",
              default=False, required=True)
@click.option("-z", "--backup", help="Backup that will be deactivated",
              default=False, required=True)
@click.option("-f", "--config_file", default=False, required=True,
              help="Config file with the database credentials")
@click.option("-s", "--admin_password", help="Password used to log in as admin in odoo",
              required=True)
@click.option("-c", "--cformat",
              help="Compression format to be used (tar.bz2 or tar.gz)",
              default='bz2', required=False)
def deactivate_backup(prefix, log_level, store_path, backup,
                      config_file, admin_password, cformat):
    logger.setLevel(log_level)
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    db_config = dict(config.items('postgres'))
    default_config = utils.load_default_config()
    command = commandv.CommandV(default_config)
    res = command.deactivate_backup(db_config, backup, prefix, store_path, cformat, admin_password)
    if not res:
        sys.exit(1)
    logger.info('Deactivated backup stored in %s', res)
    logger.info('Done')


@cli.command()
@click.option("-l", "--log_level", help="Log level to show", default='INFO')
@click.option("-f", "--config_file",
              help=("Config file where the parameters for the build will be taken from,"
                    " if the other parameters are specified, the config will be"
                    " updated accordingly. If not specified, a default config will be used."
                    " You have to use this parameter in order to build an image with more than"
                    " one base repo"))
@click.option("-u", "--repo", help="URL of the main github repository that will be used")
@click.option("-b", "--branch", help=("Branch of the repository that will be cloned."
                                      " If no branch is specified, then the version will be used"))
@click.option("-i", "--image-name",
              help=("Name of the docker image that will be used as a base to build the new image."
                    " Default: vauxoo/odoo-{version}-image"))
@click.option("-w", "--working-folder", default="deployv_build",
              help=("Name of the folder where the files required for the build will be stored"
                    "(default deployv_build)"))
@click.option("-v", "--version",
              help=("Version of the oca dependencies that will be used in the image"
                    " e.g. 8.0, 9.0, etc."))
@click.option("--force", is_flag=True, default=False,
              help="Removes the working folder if it already exists before creating it again")
@click.option("-O", "--odoo-repo",
              help=("Specific odoo repository to be cloned instead of the default one, must be"
                    " in the format namespace/reponame#branch. Example: odoo/odoo#8.0"))
@click.option("-T", "--tag", default=False,
              help="Custom name for the new image, if not specified a name will be generated")
def build(log_level, config_file, repo, branch, image_name, working_folder, version,
          force, odoo_repo, tag):
    if config_file:
        config = utils.load_json(config_file)
    else:
        config = {}
    default_config = utils.load_default_config()
    config = utils.merge_dicts(default_config, config)
    if repo and not version or version and not repo:
        logger.error('If you specify the repo or the version you have to specify'
                     ' the other one as well')
        sys.exit(1)
    if branch and not repo:
        logger.error('If you specify a branch you have to specify the repo')
        sys.exit(1)
    if not branch:
        branch = version
    if repo and branch:
        repo_name = repo.split('/')[-1].split('.')[0]
        repo_path = os.path.join('extra_addons', repo_name)
        config = build_helper.add_repo(config, branch, repo_name, repo_path, repo)
    if odoo_repo:
        if not re.search('.*/.*#.*', odoo_repo):
            logger.error('The specified odoo repo does not have the correct format.'
                         ' Example format: odoo/odoo#8.0')
            sys.exit(1)
        parts = odoo_repo.split('#')
        odoo_branch = parts[1]
        odoo_url = 'https://github.com/{repo}.git'.format(repo=parts[0])
        config = build_helper.add_repo(config, odoo_branch, 'odoo', 'odoo', odoo_url)
    if image_name:
        config.get('container_config').update({'base_image_name': image_name})
    config.get('container_config').update({'build_image': True})
    res = build_helper.build_image(config, version, working_folder, force, tag)
    if not res[0]:
        logger.error(res[1].get('error'))
        sys.exit(1)
    logger.info('Image built: %s', res[1].get('result'))
    sys.exit(0)

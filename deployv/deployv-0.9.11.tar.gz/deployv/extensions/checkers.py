# coding: utf-8
from os import path
import logging
import odoorpc
from docker.errors import APIError, NullResource, NotFound
from deployv.base import errors
from deployv.base.extensions_core import EventListenerBase
from deployv.base import postgresv
from deployv.helpers import utils
from deployv.instance import instancev

logger = logging.getLogger('deployv')  # pylint: disable=C0103


class TestPsqlConnection(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to test the connection with postgres before the instance is
        constructed so it is possible to validate the configuration parameters
        """
        name = 'CheckPsqlConnection'
        event = 'before.create.event'

    def execute(self, obj):
        psql_dict = utils.odoo2postgres(obj.instance_manager.db_config)
        logger.debug('Dict: %s', str(psql_dict))
        psql_dict.update({'dbname': 'postgres'})
        try:
            with postgresv.PostgresConnector(psql_dict) as db_test:
                res = db_test.check_config()
                if res:
                    logger.info('PostgreSQL connection test passed')
                else:
                    logger.info('PostgreSQL connection test failed')
        except Exception:  # pylint: disable=W0703
            res = False
            logger.error("Could not connect to the database")
        return res


class TestDockerUser(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener to test if the user is configured to use docker, pull images, etc
        """
        name = 'CheckDockerUser'
        event = 'before.create.event'

    def execute(self, obj):
        # Check if user can use docker
        res = False
        import getpass
        from docker import Client
        cli = Client()
        try:
            cli.containers(all=True)
        except Exception as error:  # pylint: disable=W0703
            logger.error(('Current user "%s" cannot connect to docker or'
                          ' docker service is down: %s'),
                         getpass.getuser(), error.message)
        else:
            logger.info('Docker connection test passed for user %s',
                        getpass.getuser())
            res = True
        return res


class InstallTestRepo(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to install the web_environment_ribbon if it is a test or
        dev instance
        """
        name = 'InstallTestRibbon'
        event = 'after.restore.event'

    def deploy_test_repo(self, instance):
        """Create link to the web_environment_ribbon addon meanwhile we developthe add new
        repo feature

        :param config: Config dict used to create the container and instance
        :param info: Info dict returned by start_odoo_container
        """
        try:
            res = instance.exec_cmd(('su {user} -c "ln -s {home}/instance/extra_addons/oca_web/'
                                     'web_environment_ribbon {home}/instance/odoo/addons/'
                                     'web_environment_ribbon"')
                                    .format(user=instance.docker_env.get('odoo_user'),
                                            home=instance.docker_env.get('odoo_home'))
                                    )
        except APIError as error:
            logger.exception('Could not install the test repo: %s', error.explanation)
        except errors.NotRunning as error:
            logger.exception('Container is not running: %s', error.message)
            return False
        logger.debug('Deployed the repo: %s', res)

    def execute(self, obj, returned_value):
        instance_type = obj.instance_manager.instance_type
        logger.debug('Instance type: %s', instance_type)
        if instance_type in instancev.INSTALL_RIBBON\
                and returned_value.get('result', False):
            self.deploy_test_repo(obj.instance_manager)
            res = False
            if not returned_value.get('result').get('database_name'):
                logger.error('Could not install the web_environment_ribbon, Database not found')
                return False
            elif returned_value.get('result').get('critical'):
                logger.error(returned_value.get('result').get('critical'))
                return False
            else:
                logger.debug('Installing the web_environment_ribbon')
                install = obj.instance_manager.install_module(
                    'web_environment_ribbon',
                    returned_value.get('result').get('database_name')
                )

            if len(install.get('warnings')) >= 1:
                for warn in install.get('warnings'):
                    if 'invalid module names, ignored: web_environment_ribbon' in warn:
                        obj.instance_manager.update_db(
                            'all', returned_value.get('result').get('database_name')
                        )
                        install = obj.instance_manager.install_module(
                            'web_environment_ribbon',
                            returned_value.get('result').get('database_name')
                        )
                        res = True
                        break
        else:
            res = False
        return res


class TestContainer(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener is made to test if the container is running and the instance is up,
        at this point we cannot assume that there is a database because is just a post event for
        :meth:`deployv.base.commandv.CommandV.create` method and such method does not create
        database
        """
        name = 'CheckContainer'
        event = 'after.create.event'

    def execute(self, obj, returned_value):
        if obj.instance_manager.docker_id is None:
            return False
        cid = obj.instance_manager.docker_id
        try:
            inspected = obj.instance_manager.inspect()
        except NotFound:
            logger.exception('The provided id/name does not exists')
            return False
        except NullResource as error:
            logger.exception('Container is not running: %s',
                             utils.get_error_message(error))
            return False
        except errors.NoSuchContainer as error:
            logger.exception('Container does not exists: %s', utils.get_error_message(error))
            return False

        if not inspected.get('State').get('Running'):
            logger.error('The container %s is not runnig', cid)
            return False

        # Check if odoo instance is running
        res = obj.instance_manager.exec_cmd('supervisorctl status odoo')
        if 'RUNNING' not in res:
            logger.error('Odoo instance is not running in container %s', cid)
        else:
            logger.info(
                'Supervisord in container %s reported the instance is running', cid)
        info = obj.instance_manager.basic_info
        try:
            odoo = odoorpc.ODOO(obj.instance_manager.config.get(
                'domain'), port=info.get('ports').get('8069'))
            odoo.db.list()
        except Exception as error:  # pylint: disable=W0703
            logger.error('Could not connect to the instance using %s:%s',
                         obj.instance_manager.config.get('domain'),
                         info.get('ports').get('8069'))
            logger.error(error.message)
            res = False
        else:
            logger.info('Connected to the instance via %s:%s',
                        obj.instance_manager.config.get('domain'),
                        info.get('ports').get('8069'))
            res = True
        return res


class TestBranches(EventListenerBase):

    class Meta:  # pylint: disable=C1001
        """ This EventListener makes sure that the branches and commits cloned into the new
        instance are the ones specified in branchesv
        """
        name = 'CheckBranches'
        event = 'after.create.event'

    def execute(self, obj, returned_value):
        try:
            pre_path = path.join(obj.instance_manager.temp_folder, 'branches.json')
        except APIError as error:
            logger.exception('Could not connect to the instance: %s', error.explanation)
            return False
        except errors.NotRunning as error:
            logger.exception('Container is not running: %s',
                             utils.get_error_message(error))
            return False
        except errors.NoSuchContainer as error:
            logger.exception('Container does not exists: %s', utils.get_error_message(error))
            return False

        try:
            pre_branches = utils.load_json(pre_path)
        except IOError as error:
            logger.warn(utils.get_error_message(error))
            logger.warn('Maybe no branches was provided in the config (this is not an error)')
            return True
        home = obj.instance_manager.config.get('env_vars').get('odoo_home')
        instance_dir = path.join(home, 'instance/')
        post_path = path.join('/tmp', 'post_process.json')
        try:
            obj.instance_manager.exec_cmd('branchesv save -p {i} -f {p}'.format(i=instance_dir,
                                                                                p=post_path))
        except errors.NotRunning as error:
            logger.exception('Could not load the branches: %s',
                             utils.get_error_message(error))
            return False
        post_branches = utils.load_json(
            path.join(
                obj.instance_manager.temp_folder,
                'post_process.json'
            ))
        for value in pre_branches:
            if not value['commit']:
                url_dict = value['repo_url']
                url = url_dict.get('origin')
                cmd = ('git ls-remote {remote} HEAD'.format(remote=url))
                result = obj.instance_manager.exec_cmd(cmd)
                latest = result.split()
                value['commit'] = latest[0].strip()
            if value not in post_branches:
                logger.info('Repository not cloned: %s', value['name'])
            else:
                logger.info('Repository %s successfully cloned', value['name'])

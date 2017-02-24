from deployv.helpers import utils
from deployv.helpers.clone_oca_dependencies import run as clone_oca_deps
from deployv.base.errors import BuildError
from deployv.instance import ODOO_BINARY
from docker import Client
from jinja2 import Environment, FileSystemLoader
from os import path
from tempfile import mkdtemp
import shutil
import logging
import simplejson as json
import spur
from branchesv import utils as branches_utils


_logger = logging.getLogger('deployv')


class BuildImage(object):

    def __init__(self, config, version, working_folder='/tmp',
                 force=False, full_stack_image=False, tag=False):
        """
            :param config: Config dictionary with the format used by deployv.
            :param version: Branch that will be used to clone all the oca dependencies.
                            e.g 8.0, 9.0, etc.
            :param working_folder: Working dir where all the files necessary for the build
                                   will be stored. Default /tmp
            :param force: If true, will remove any directory with the same name as the
                          working directory in the path specified before trying to create
                          the working directory. Default False
            :param full_stack_image: If True, creates a new image with full stack tools, that is:
                                     - PostgreSQL
                                     - Nginx
                                     - Supervisor
                                     - Odoo
                                     - Openssh-server
        """
        self.client = Client()
        self._config = config
        self.version = version
        self.working_folder = utils.decode(working_folder)
        self.force = force
        self.full_stack_image = full_stack_image
        if not tag:
            tag = self._generate_image_name()
        self.new_image_name = tag
        if full_stack_image:
            self.base_image_name = self._config.get('container_config').get('image_name')
        elif self._config.get('container_config').get('base_image_name'):
            self.base_image_name = self._config.get('container_config').get('base_image_name')
        else:
            self.base_image_name = utils.clean_string(
                'vauxoo/odoo-{ver}-image'.format(ver=self.version.replace('.', '')))
        self._templates_path = utils.decode(
            path.join(path.dirname(utils.decode(path.abspath(__file__))),
                      '..',
                      'templates'))
        self.files_path = path.join(self._templates_path, 'files')

    def _generate_image_name(self):
        """ Generates the name that the new image will have depending on the parameters
        used to build it, the name is created as follows:

        - Exactly one repo: { repo_name }-{ repo_branch }
        - Zero or more than one repo: { task_id }_{ customer_id }_image
        - full_stack_image = True: { task_id }_full_odoo_stack

        :return: New image name
        """
        repositories = list(self._config.get('instance').get('repositories'))
        if self.full_stack_image:
            name = '{tid}_full_odoo_stack'.format(tid=self._config.get('instance')
                                                          .get('task_id'))
        elif self._config.get('container_config').get('start_postgres_image'):
            name = '{tid}_postgres_image'.format(tid=self._config.get('instance')
                                                 .get('task_id'))
        elif len(repositories) == 1:
            repo = repositories[0]
            name = '{repo}{branch}'.format(repo=repo.get('name'), branch=repo.get('branch'))
        elif len(repositories) == 2:
            for repo in repositories:
                if repo.get('name') == 'odoo':
                    repositories.remove(repo)
                    name = '{repo}{branch}'.format(repo=repositories[0].get('name'),
                                                   branch=repositories[0].get('branch'))
                    break
            else:
                name = '{tid}_{cid}_image'.format(tid=self._config.get('instance')
                                                                  .get('task_id'),
                                                  cid=self._config.get('instance')
                                                                  .get('customer_id'))
        else:
            name = '{tid}_{cid}_image'.format(tid=self._config.get('instance').get('task_id'),
                                              cid=self._config.get('instance').get('customer_id'))
        return utils.clean_string(name)

    def _render_odoo_service(self):
        """ Render the supervisor configuration file for Odoo depending on the version

        :return: None
        """
        env = Environment(loader=FileSystemLoader(self._templates_path))
        template = env.get_template('odoo_service.conf.jinja')
        service_file = template.render({'odoo_binary': ODOO_BINARY[self.version]})
        _logger.debug('Rendering supervisor config for Odoo %s', self.version)
        with open(path.join(
                utils.encode(self._files_folder), 'odoo_service.conf'), 'w') as text_file:
            text_file.write(service_file)

    def _create_working_folder(self):
        """ Creates the working directory with the needed subdirectories and
            copies the files that will be used for the build.

            :return: dictionary containing the paths created inside the working folder
        """
        res = {}
        if path.isdir(self.working_folder) and self.force:
            shutil.rmtree(utils.encode(self.working_folder))
        utils.makedir(self.working_folder)
        self.working_folder = utils.decode(
            mkdtemp(prefix='build_', dir=utils.encode(self.working_folder)))
        self._files_folder = path.join(self.working_folder, 'files')
        try:
            shutil.copytree(
                utils.encode(self.files_path),
                utils.encode(self._files_folder))
        except OSError:
            _logger.error('The specified working folder already exists and it is not empty,'
                          ' use --force to remove it')
            raise
        self._render_odoo_service()
        instance_path = path.join(self._files_folder, 'instance')
        extra_path = path.join(instance_path, 'extra_addons')
        utils.makedir(utils.encode(instance_path))
        utils.makedir(utils.encode(extra_path))
        res.update({'instance': instance_path, 'extra_addons': extra_path})
        return res

    def _search_odoo_repo(self):
        """ Iterates over the repositories that will be used for the build to see
        if the odoo repo is specified or not by checking if a repo will be cloned in the
        path expected by supervisor. This is used to know whether to clone
        the default vauxoo/odoo repo or not.

        :return: dict with the info of the odoo repo if the odo repo was specified by the user
                 in the correct path, default one otherwise
        """
        res = {
            "branch": self.version,
            "repo_url": {
                "origin": "https://github.com/Vauxoo/odoo.git"
            }
        }
        for repo in self._config.get('instance').get('repositories'):
            if repo.get('name') == 'odoo' and repo.get('path') == 'odoo':
                res = repo
                break
        return res

    def _clone_dependencies(self, instance_path, extra_path):
        """ Clones the repo odoo, the repositories specified in the config and
            all their oca dependencies inside the working folder.

            :param instance_path: Path to the instance folder where the odoo repo will be cloned.
            :param extra_path: Path to the extra_addons folder that will contain all of the other
                               repos that will be cloned (base repo and oca dependencies).
            :return: True if no error is raised.
        """
        odoo_repo = self._search_odoo_repo()

        utils.clone_repo(odoo_repo.get('repo_url').get('origin'), odoo_repo.get('branch'),
                         path.join(instance_path, 'odoo'))
        try:
            self._config.get('instance').get('repositories').remove(odoo_repo)
        except ValueError:
            pass

        for repo in self._config.get('instance').get('repositories'):
            if not repo.get('branch'):
                repo.update({'branch': self.version})
            repo_name = repo.get('name') if repo.get('name', False) else\
                branches_utils.name_from_url(repo.get('repo_url').get('origin'))
            utils.clone_repo(repo.get('repo_url').get('origin'), repo.get('branch'),
                             path.join(extra_path, repo_name))
        clone_oca = clone_oca_deps(extra_path, extra_path, self.version)
        if not clone_oca[0]:
            raise BuildError(clone_oca[1])
        return True

    def _create_image(self, template, values):
        """ Build a new image using a Dockerfile created by rendering a template with the
            parameters provided by the user.

            :param template: name of the template that will be used to create the dockerfile,
                             Dockerfile.jinja for the full stack image and build_dockerfile.jinja
                             for the image with the repos and their oca dependencies.
            :param values: values used to render the template

            :return: Name of the new image.
        """
        _logger.info('pulling base image %s', self.base_image_name)
        self.client.pull(self.base_image_name)
        env = Environment(loader=FileSystemLoader(self._templates_path))
        template = env.get_template(template)
        docker_file = template.render(values)
        with open(path.join(utils.encode(self.working_folder), 'Dockerfile'), 'w') as text_file:
            text_file.write(docker_file)
        _logger.info('Building image')
        for line in self.client.build(path=utils.encode(self.working_folder),
                                      timeout=3600, rm=True,
                                      tag=self.new_image_name):
            obj = json.loads(line)
            if obj.get('stream'):
                _logger.info(obj.get('stream').strip())
            elif obj.get('error'):
                raise BuildError(obj.get('error').strip())

    def build(self):
        """ Main method that builds the new image using the information
            provided by the user.

            :return: Dictionary with the name of the new image
        """
        res = {}
        _logger.info('Building image')
        try:
            paths = self._create_working_folder()
        except IOError, error:
            res.update({'error': utils.get_error_message(error)})
            return res
        if self.full_stack_image:
            values = {
                'base_image_name': self.base_image_name,
                'db_user': self._config.get('instance').get('config').get('db_user'),
                'db_password': self._config.get('instance').get('config').get('db_password')
            }
            template = 'Dockerfile.jinja'
        else:
            try:
                self._clone_dependencies(paths['instance'], paths['extra_addons'])
            except spur.results.RunProcessError, error:
                res.update({"error": utils.get_error_message(error)})
                return res
            except BuildError as error:
                _logger.exception('Could not clone the repos: %s', utils.get_error_message(error))
                res.update({'error': utils.get_error_message(error)})
                return res
            values = {'version': self.version, 'base_image_name': self.base_image_name}
            template = 'build_dockerfile.jinja'
        try:
            self._create_image(template, values)
        except IOError, error:
            res.update({'error': utils.get_error_message(error)})
            return res
        except BuildError as error:
            error = utils.get_error_message(error)
            if "This image has already been build with deployv" in error:
                error = ('An image that has already been built with deployv'
                         ' can\'t be used to build another image.')
            res.update({'error': error})
            return res
        res.update({'result': self.new_image_name})
        return res


def add_repo(config, branch, name, repo_path, repo_url):
    """ Creates a dictionary with the info of the specified repo and
    appends it to the repositories list in the config dictionary

    :param config: Config dict where the new repo will be added
    :param name: Name of the repository
    :param path: Path inside ~/instance where the repository will be cloned
    :param repo_url: ssh or https URL used to clone the repo
    :param branch: branch of the repo we want to clone
    :return: Config dict with the new repo
    """
    repo_dict = {
        'branch': branch,
        'name': name,
        'path': repo_path,
        'repo_url': {
            'origin': repo_url
        }
    }
    config.get('instance').get('repositories').append(repo_dict)
    return config


def build_image(config, version=False, working_folder='/tmp', force=False, tag=False):
    """ Calls the build helper class with the needed parameters depending if
    a new full stack image, develop image or both will be created.
    If the config dictionary has both, build_image = true and postgres_container = true,
    first it will build a new image with the repos specified in the config and their
    oca dependencies, then that image will be used as base in order to build another one
    with the full stack tools.

    :param config: Configuration dictionary with the format used by deployv.
    :param version: Version that will be used to clone the oca dependencies, e.g. 8.0, 9.0
    :param working_folder: Working folder where the files required for the build
                           will be stored.
    :param force: If true and the specified working folder exists, it will be removed
                  before trying to create it again.
    :return: dictionary with the new image created or an error.
    """
    build_res = {}
    if not version:
        version = utils.version_cid(config.get('instance').get('customer_id'))
        if version is None:
            return (False, {'error': ('You need to specify the customer id with the correct format'
                                      ' or use the version parameter. Example: customer80')})
    _logger.debug('Starting the build image process with:')
    _logger.debug(json.dumps(config, sort_keys=True, indent=2))
    if config.get('container_config').get('build_image'):
        _logger.debug('Building single image')
        build_class = BuildImage(config, version, utils.decode(working_folder), force, tag=tag)
        build_res = build_class.build()
        if build_res.get("error"):
            return (False, build_res)
        config.get('container_config').update({'image_name': build_res.get('result')})
    if config.get('container_config').get('full_stack'):
        _logger.debug('Building full image')
        build_class = BuildImage(config, version, utils.decode(working_folder),
                                 force, full_stack_image=True, tag=tag)
        build_res = build_class.build()
        if build_res.get("error"):
            return (False, build_res)
    return (True, build_res)

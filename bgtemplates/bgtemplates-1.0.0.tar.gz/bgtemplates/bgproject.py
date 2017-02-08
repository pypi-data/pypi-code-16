"""
Utilities related to the project creation and the render of the files.

*.bgtpl* are considered the templates. The rendering is done using a
:class:`BGProject` object with is a namespace containing all the possible
names needed by the templates.
The final extension of the file should precede the *.bgtpl* extension.

In is the responsibility of the :file:`template.py` script of each
project template to create and fill the :class:`BGProject` object.
"""

import os
import shutil
import logging
from types import SimpleNamespace
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2.loaders import split_template_path
from jinja2.utils import open_if_exists

from bgtemplates.utils import remove_file


class BGProject(SimpleNamespace):
    """
    Container class for objects used in the templates rendering
    """

    def __init__(self):
        super(BGProject, self).__init__()

        self.cli_enabled = False

    def enable_cli_as(self, cmd):
        self.cli = cmd
        self.cli_enabled = True


class JinjaLoader(FileSystemLoader):
    """
    Override the Jinja :class:`~jinja2.FileSystemLoader`
    but only including our template files
    """

    @staticmethod
    def is_template(file):
        """
        Check if a file is a template

        Args:
            file (str): path to a file

        Returns:
            bool. Wheter the file is a template or not

        """
        _, ext = os.path.splitext(file)
        return ext == '.bgtpl'

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = os.path.join(searchpath, *pieces)
            if not JinjaLoader.is_template(filename):
                continue
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = os.path.getmtime(filename)

            def uptodate():
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, dirnames, filenames in walk_dir:
                for filename in filenames:
                    if not JinjaLoader.is_template(filename):
                        continue
                    template = os.path.join(dirpath, filename) \
                        [len(searchpath):].strip(os.path.sep) \
                                          .replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)


def render_templates(folder, project):
    """
    Renders all templates in a folder

    Args:
        folder (str): path to a folder
        project (:class:`BGProject`): namespace with the variables used during the rendering process

    """
    logging.debug('rendering templates')
    env = Environment(loader=JinjaLoader(folder))
    env.globals['project'] = project
    for file in env.list_templates():
        new_file, _ = os.path.splitext(file)
        template = env.get_template(file)
        with open(os.path.join(folder,new_file), 'w') as fd:
            fd.write(template.render())
        remove_file(os.path.join(folder, file))


def create_project_structure(base_dir, project, unwanted_files=('__init__.py', 'template.py', 'project_doc.rst'), unwanted_dirs=('__pycache__')):
    """
    Creates the project from a template project

    Args:
        base_dir (str): path of the template project
        project (str): path where to create the new project

    Workflow:
    #. Copy the template project
    #. Remove unnecessary files
    #. Rename files & folders
    #. Render the templates inside the project

    """

    logging.info('Creating the project files')

    logging.debug('Copying files')
    destination = shutil.copytree(base_dir, project.path)

    logging.debug('Removing unwanted files')
    # remove files
    for file in unwanted_files:
        remove_file(os.path.join(destination, file))

    for d in unwanted_dirs:
        shutil.rmtree(os.path.join(destination, d), ignore_errors=True)

    logging.debug('Renaming mypackage')
    # rename the package
    shutil.move(os.path.join(destination, 'mypackage'), os.path.join(destination, project.name))

    # render the templates
    render_templates(destination, project)

import os
import click

from bgtemplates.bgproject import BGProject, create_project_structure
from bgtemplates.click_utils import ask_for_cli, find_conda, ask_for_path, click_check_project_name
from bgtemplates.conda import create_env
from bgtemplates.git import create_repo
from bgtemplates.tips import Tip, show_tips
from bgtemplates.utils import install_developer_mode
from . import __version__

CONDA_PACKAGES = ['numpy', 'pandas', 'matplotlib', 'scipy']


@click.command(short_help='Creates the basic structure for a scienfitic project with Python')
@click.option('--name', '-n', prompt='Name of the project', callback=click_check_project_name, help='Name of your project')
@click.version_option(version=__version__)
def pydata(name):
    """Create a Python project with basic scientific libraries"""

    project = BGProject()
    project.name = name

    project.path = ask_for_path(project.name)

    conda_packages = CONDA_PACKAGES

    cmd = ask_for_cli(project.name)
    if cmd is not None:
        project.enable_cli_as(cmd)
        conda_packages.append('click')

    project.unversioned_packages = conda_packages
    project.versioned_packages = {}

    conda_env_path = None
    conda = find_conda()
    if conda is not None:
        env = create_env(conda, name, conda_packages)
        if env is not None:
            conda_env_name, conda_env_path, packages = env
            project.unversioned_packages = []
            project.versioned_packages = packages

    unwanted_files = ['__init__.py', 'template.py', 'project_doc.rst']
    unwanted_dirs = ['__pycache__', 'mypackage/__pycache__']
    base_dir = os.path.dirname(os.path.abspath(__file__))
    create_project_structure(base_dir, project, unwanted_files, unwanted_dirs)

    if conda_env_path is not None:
        pip_path = os.path.join(conda_env_path, 'bin', 'pip')
        install_developer_mode(pip_path, project.path)

    create_repo(project.path)

    show_tips()

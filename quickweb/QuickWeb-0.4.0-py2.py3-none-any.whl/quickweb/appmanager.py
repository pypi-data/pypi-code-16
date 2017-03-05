"""
The app manager module
"""
from __future__ import print_function
import os
from os.path import exists, join, basename, isdir
from glob import glob
import shutil
import sys

from quickweb._tempfile import TemporaryDirectory
from quickweb.templatemanager import TemplateMaker, Downloader

def deploy(app_directory, target_url):
    """
    Deploy application to target url
    """
    print("Deploying")
    with TemporaryDirectory() as tmpdirname:
        for location in ['webroot', 'template']:
            print(" %s -> %s " % (join(app_directory, location), join(tmpdirname, location)))
            shutil.copytree(join(app_directory, location), join(tmpdirname, location))
        required_files = ['requirements.txt', 'app.py']
        for filename in required_files:
            source_file = join(os.path.dirname((os.path.realpath(__file__))), '..', filename)
            print("%s -> %s" % (source_file, join(tmpdirname, filename)))
            shutil.copy(source_file, join(tmpdirname, filename))
        source_dir = join(os.path.dirname((os.path.realpath(__file__))), '..', 'quickweb')
        print("%s -> %s" % (source_dir, join(tmpdirname, 'quickweb')))
        shutil.copytree(source_dir, join(tmpdirname, 'quickweb'))
        os.chdir(tmpdirname)
        os.system('git init')
        os.system('git add . ')
        os.system('git commit -m "First commit"')
        os.system('git remote add origin '+target_url)
        os.system('git push origin master --force ')


def init(app_directory, template_name, force):
    """
    Create app from template
    """
    print("***** Creating app on directory", app_directory)
    app_core_directories = ('webroot', 'libs')
    if exists(app_directory):
        if force:
            shutil.rmtree(app_directory)
        else:
            sys.stderr.write(app_directory + ' already exists!\n')
            sys.exit(2)
    print("Downloading template", template_name)
    Downloader(template_name, app_directory).download(force)
    for directory in app_core_directories:
        core_dir = join(app_directory, directory)
        print("- Creating app core directory", core_dir)
        if not exists(core_dir):
            os.makedirs(core_dir, mode=0o755)

    print("Copying base python start files")
    required_files = glob(join('/', 'usr', 'share', 'quickweb', '*'))
    for filename in required_files:
        shutil.copy(filename, app_directory)
    print("App Created.")


def make_template(template_url, template_directory, force):
    """ return template from Mako template maker """
    TemplateMaker(template_url, template_directory).make(force)


def git_init(app_directory, git_url, force):
    """ git init repo """
    os.chdir(app_directory)
    if exists('.git') and not force:
        sys.stderr.write("Git is already setup for this application.\n")
        sys.exit(2)

    os.system('git init')
    os.system('git add . ')
    os.system('git commit -m "First commit"')
    os.system('git remote add origin '+git_url)
    os.system('git remote -v')
    os.system('git push origin master --force')

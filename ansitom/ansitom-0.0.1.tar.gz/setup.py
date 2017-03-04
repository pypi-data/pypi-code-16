from setuptools import setup, find_packages
from pip.req import parse_requirements
import os

# reading requirements from requirements.txt
dir_path = os.path.dirname(os.path.realpath(__file__))
reqs_file = 'requirements.txt'.format(dir_path)
with open(reqs_file) as f:
    required = f.read().splitlines()

ignore_dir = ['.git']

setup(
    name='ansitom',
    version='0.0.1',
    description = 'Ansible playbook generator',
    author = 'samvaran kashyap rallabandi',
    author_email = 'samvaran.kashyap@gmail.com',
    url = '',
    setup_requires=required,
    install_requires=required,
    entry_points='''
        [console_scripts]
        ansitom=ansitom:cli
    ''',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
)

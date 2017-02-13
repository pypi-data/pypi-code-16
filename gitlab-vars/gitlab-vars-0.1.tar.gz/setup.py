import pathlib
from setuptools import setup, find_packages

ROOT = pathlib.Path(__file__).parent

with open(ROOT / 'README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='gitlab-vars',
    version='0.1',
    description='Manage GitLab secret variables with CLI',
    long_description=readme,
    license='BSD',
    author='various',
    author_email='intrrpt@ya.ru',
    url='https://github.com/deniskrishna/gitlabvars',
    py_modules=['cli', 'client', 'colors', 'utils', 'basecommand'],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        vars=cli:main
    '''
)

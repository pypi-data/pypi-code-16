#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'aws-monocyte',
        version = '0.3.497-259',
        description = 'Monocyte - Search and Destroy unwanted AWS Resources relentlessly.',
        long_description = "\n    Monocyte is a bot for destroying AWS resources in non-EU regions written in Python using Boto.\n    It is especially useful for companies that are bound to European privacy laws\n    and for that reason don't want to process user data in non-EU regions.\n    ",
        author = 'Jan Brennenstuhl, Arne Hilmann',
        author_email = 'jan@brennenstuhl.me, arne.hilmann@gmail.com',
        license = 'Apache License 2.0',
        url = 'https://github.com/ImmobilienScout24/aws-monocyte',
        scripts = ['scripts/monocyte'],
        packages = [
            'monocyte',
            'monocyte.plugins',
            'monocyte.handler'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Programming Language :: Python',
            'Topic :: System :: Networking',
            'Topic :: System :: Software Distribution',
            'Topic :: System :: Systems Administration'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'boto',
            'boto3',
            'docopt',
            'mock',
            'pils',
            'python-cloudwatchlogs-logging',
            'yamlreader'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )

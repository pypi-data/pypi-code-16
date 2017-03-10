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
        name = 'PyBarCodeScan',
        version = '0.1.64',
        description = '''Scan tool''',
        long_description = '''Scan tool''',
        author = "Christian Franke",
        author_email = "chriss@frankeonline.net",
        license = 'APACHE LICENSE, VERSION 2.0',
        url = 'https://github.com/cfranke/scan',
        scripts = [
            'scripts/barcodescanner_reader',
            'scripts/barcodescanner_server'
        ],
        packages = ['barcodescan'],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [
            ('/etc/systemd/system/', ['barcodescan/barcodescanner_server.service', 'barcodescan/barcodescanner_reader.service'])
        ],
        package_data = {
            'barcodescan': ['templates/*']
        },
        install_requires = [
            'Flask',
            'click',
            'configparser',
            'flask-sse',
            'gevent',
            'gunicorn',
            'httplib2',
            'itsdangerous',
            'jinja2',
            'redis',
            'six',
            'werkzeug'
        ],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )

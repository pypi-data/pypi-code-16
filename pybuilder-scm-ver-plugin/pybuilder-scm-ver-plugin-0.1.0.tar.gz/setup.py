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
        name = 'pybuilder-scm-ver-plugin',
        version = '0.1.0',
        description = '''pybuilder plugin to set project from SCM''',
        long_description = '''''',
        author = "Kyrylo Shpytsya",
        author_email = "kshpitsa@gmail.com",
        license = 'MIT',
        url = 'https://github.com/kshpytsya/pybuilder-scm-ver-plugin',
        scripts = [],
        packages = ['pybuilder_scm_ver_plugin'],
        py_modules = [],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Version Control'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['setuptools_scm'],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )

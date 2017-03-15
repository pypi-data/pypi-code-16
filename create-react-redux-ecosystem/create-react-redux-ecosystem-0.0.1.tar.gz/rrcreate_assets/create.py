#!/usr/bin/env python3
import os
import shutil
import subprocess


templates = [
    'package.json',
    '.babelrc',
    '.eslintrc.js',
    '.eslintignore',
    '.flowconfig',
    '.gitignore',
    'webpack.config.js',
    'README.md',
    'index.js'
]

directories = [
    '__test__',
    'src',
    'src/actions',
    'src/components',
    'src/containers',
    'src/reducers',
    'src/store',
]

r_path = os.path.realpath(__file__)
orig_dir = '/'.join(r_path.split('/')[:-1])

dest = '.'

def mkdir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def yarn_install():
    subprocess.run(['yarn'])

def main(source='redux'):
    for dir_name in directories:
        mkdir('/'.join([dest, dir_name]))

    for t in templates:
        shutil.copy('/'.join([orig_dir, source, t]), dest)

    yarn_install()

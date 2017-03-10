from setuptools import setup, find_packages

setup(
    name="serapeum.backup",
    version="1.0.6",
    author="Pieter De Praetere",
    author_email="pieter.de.praetere@helptux.be",
    packages=[
        "serapeum.backup",
        "serapeum.backup.modules.config",
        "serapeum.backup.modules.ds",
        "serapeum.backup.modules.files",
        "serapeum.backup.modules.log",
        "serapeum.backup.modules.mail",
        "serapeum.backup.modules.mysql",
        "serapeum.backup.modules.rdiff",
        "serapeum.backup.modules.remotes",
        "serapeum.backup.modules.run",
        "serapeum.backup.modules"
    ],
    url='https://github.com/pieterdp/serapeum.backup',
    license='GPLv3',
    description="Backup script based on rdiff-backup.",
    long_description=open('README.txt').read(),
    scripts=[
        'bin/serapeum-backup'
    ],
    package_data={
        '': [
            'config/example.ini',
            'remotes/list.json',
            'selection/sources.json',
            'selection/excludes.json'
        ]
    }
)

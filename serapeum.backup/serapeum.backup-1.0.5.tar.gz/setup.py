from setuptools import setup

setup(
    name="serapeum.backup",
    version="1.0.5",
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
    data_files=[
        ('config', ['config/example.ini']),
        ('remotes', ['remotes/list.json']),
        ('selection', ['selection/sources.json', 'selection/excludes.json'])
    ]
)

import os
from setuptools import find_packages,setup
from subprocess import check_output

setup(
    description='Viking Makt WebSocket Protocol',
    install_requires=[
        'rask'
    ],
    license='https://gitlab.com/vikingmakt/rask_raid/raw/master/LICENSE',
    maintainer='Umgeher Torgersen',
    maintainer_email='me@umgeher.org',
    name='rask_raid',
    packages=find_packages(),
    url='https://gitlab.com/vikingmakt/rask_raid',
    version='0.1.0'
)

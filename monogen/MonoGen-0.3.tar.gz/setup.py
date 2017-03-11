from pathlib import Path
from setuptools import setup

DIST_NAME = 'MonoGen'
VERSION = '0.3'
AUTHOR = 'David Christenson'
EMAIL = 'mail@noctem.xyz'
GITHUB_USER = 'Noctem'
GITHUB_URL = 'https://github.com/{}/{}'.format(GITHUB_USER, DIST_NAME)


setup(
    name=DIST_NAME,
    packages=['monogen'],
    version=VERSION,
    description='Bulk PTC account creator.',
    long_description='MonoGen creates PTC accounts by creating a chrome session and automatically entering data in the required fields.',
    author=AUTHOR,
    author_email=EMAIL,
    url=GITHUB_URL,
    license='GPL v3',
    download_url='{}/releases'.format(GITHUB_URL),
    install_requires=[
        'requests[security]>=2.10.0',
        'selenium>=2.53.6'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    entry_points={
        'console_scripts': [
            'monogen = monogen.console:entry',
        ],
    }
)

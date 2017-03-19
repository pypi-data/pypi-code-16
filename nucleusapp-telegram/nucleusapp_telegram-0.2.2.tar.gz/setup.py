from distutils.core import setup

from setuptools import PackageFinder

from nucleusapp_telegram import __version__ as version

LIB_NAME = 'nucleusapp_telegram'
setup(
    name='nucleusapp_telegram',
    version=version,
    packages=PackageFinder.find(),
    url='https://bitbucket.org/illemius/nucleusapp_telegram',
    license='MIT',
    author='Illemius/Alex Root Junior',
    author_email='jroot.junio@gmail.com',
    description='Telegram module for NucleusApp based on pyTelegramBotAPI',
    keywords=[
        'Illemius',
        'NucleusUtils',
        'NucleusApp',
        'Telegram'
        'Utilities'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    install_requires=[
        'NucleusApp',
        'NucleusUtils',
        'pyTelegramBotAPI',
        'TeleSocketClient'
    ]
)

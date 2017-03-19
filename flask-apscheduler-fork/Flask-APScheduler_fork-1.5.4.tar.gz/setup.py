"""Temporary package for my own usage. Notice different requirements: apscheduler==3.0.5"""

from setuptools import setup

setup(
    name='Flask-APScheduler_fork',
    version='1.5.4',
    packages=['flask_apscheduler'],
    url='https://github.com/eayin2/flask-apscheduler',
    license='Apache 2.0',
    author='Eayin',
    author_email='eayin2@gmail.com',
    description='Test package and a fork of flask_apscheduler.',
    keywords=['apscheduler', 'scheduler', 'scheduling', 'cron'],
    install_requires=['flask>=0.10.1', 'apscheduler==3.0.5', 'python-dateutil>=2.4.2'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)

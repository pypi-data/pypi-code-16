#!/usr/bin/env python

from setuptools import setup


setup(
    name='Flask-FDS',
    version='0.0.4',
    url='https://coding.net/u/lvzhaoxing/p/Flask-FDS',
    license='MIT',
    author='Lv Zhaoxing',
    author_email='lvzhaoxing@qq.com',
    description='Xiaomi File Storage Service for Flask',
    long_description='Xiaomi File Storage Service for Flask. Please visit: https://coding.net/u/lvzhaoxing/p/Flask-FDS',
    py_modules=['flask_fds'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    keywords='fds for flask',
    #packages=['flask_fds'],
    package_data={'': ['LICENSE']},
    install_requires=[
        'setuptools',
        'Flask',
        'galaxy-fds-sdk'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

import os
import sys

from setuptools import find_packages, setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = find_packages()

setup(
    name='django-cbr',
    version='0.1.1',
    description='Load currencies rate from CBR site to Django model',
    long_description='Simply load currencies from Central Bank of Russia site (http://www.cbr.ru/scripts/XML_daily.asp) to Django model',
    author='Slava M',
    author_email='master@neucom.ru',
    url='https://github.com/slavama/django-cbr',
    packages=packages,
    include_package_data=True,
    py_modules=['cbr'],
    requires = ['python (>= 2.7)', 'django (>= 1.8)'],
    install_requires=[
        'requests>=2'
    ],
    license='MIT License',
    zip_safe=False,
    keywords='currency rate cbrf load',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)

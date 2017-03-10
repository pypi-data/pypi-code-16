import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'Django>=1.8',
    'django-appconf',
    'djangorestframework>=3.1.0',
]

setup(
    name='django-user-report',
    version='1.0.4',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    license='MIT License',  # example license
    description='A simple user content report system with RESTful api and Email Notification.',
    long_description=README,
    url='https://github.com/DrChai/django-user-report',
    author='Edward Chai',
    author_email='edwardc@acrossor.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
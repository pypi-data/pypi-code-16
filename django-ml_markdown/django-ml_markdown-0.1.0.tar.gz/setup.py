from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-ml_markdown',

    version='0.1.0',

    description='A django app that parse markdown to html',
    long_description=long_description,

    url='https://github.com/maxlothaire/django-ml_markdown',

    author='Max Lothaire',

    author_email='maxlothaire@gmail.com',

    license='BSD',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',

        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='django markdown ml_markdown',

    packages=find_packages(exclude=['ml_markdown.tests']),

    install_requires=[
        'misaka',
        'pygments',
        'bleach'
    ]
)

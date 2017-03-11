# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django_i18nize',
    version='0.0.2',
    author=u'Mohammed Hammoud',
    author_email='mohammed@iktw.se',
    packages=find_packages(),
    url='https://github.com/iktw/i18nize-django',
    license='MIT licence, see LICENCE.txt',
    description='Django i18nize extends the i18nize python client. Template tag for rendering translation and Management command for fetching  translations is added.',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'i18nize',
    ],
)
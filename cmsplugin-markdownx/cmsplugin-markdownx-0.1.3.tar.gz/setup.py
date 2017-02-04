import os
from setuptools import setup, find_packages
import cmsplugin_markdownx


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="cmsplugin-markdownx",
    version=cmsplugin_markdownx.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.md'),
    url="https://github.com/bobhy/cmsplugin-markdownx",
    author='Bob Hyman',
    author_email='bob.hyman@bobssoftwareworks.com',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment ',
        'Framework :: Django ',
        'Framework :: Django :: 1.10 ',
        'Framework :: Django :: 1.9 ',
        'Intended Audience :: Developers ',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent ',
        'Programming Language :: Python ',
        'Programming Language :: Python :: 3.3 ',
        'Programming Language :: Python :: 3.4 ',
        'Programming Language :: Python :: 3.5 ',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content ',
        'Topic :: Software Development ',
        'Topic :: Software Development :: Libraries :: Application Frameworks ',
        'Topic :: Text Processing :: Markup',
        ],
    keywords='django, django-cms, plugin, markdown, editor',
    packages=find_packages(),
    install_requires=[
        'Django (>1.8, <1.11)',
        'django-cms (<=3.4.2)',
        'django-markdownx (<1.7.2)',
        'Markdown (<2.6.8)',
        'Pygments (>2.0)',
    ],
    platforms=['OS Independent'],
    include_package_data=True,
    
)

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='app-d',
    packages=find_packages(),
    version='0.2.3',
    description='Automated Python Push-Deploy',
    long_description=long_description,
    py_modules=['app_d', 'server'],
    author='Ivo Janssen',
    author_email='hello@ivo.la',
    url='https://github.com/foxxyz/app-d',
    download_url='https://github.com/foxxyz/app-d/tarball/0.2.3',
    keywords=['deployment', 'git', 'push-deploy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
    install_requires=['paramiko'],
    entry_points={
        'console_scripts': [
            'app-d=app_d:main',
        ]
    }
)

import re
from setuptools import setup, find_packages


with open('tmpld/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst') as fd:
    long_description = fd.read()


setup(
    name='tmpld',
    version=version,
    description='Render templates in docker entrypoint scripts.',
    long_description=long_description,
    keywords=[
        'kubernetes',
        'clustering',
        'entrypoint',
        'entrypoints',
        'docker',
        'template',
        'templates'
    ],
    author='Joe Black',
    author_email='joeblack949@gmail.com',
    url='https://github.com/joeblackwaslike/tmpld',
    download_url=(
        'https://github.com/joeblackwaslike/tmpld/tarball/%s' % version),
    license='Apache 2.0',
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    install_requires=[
        'pyrkube',
        'pycaps',
        'cement',
        'Jinja2',
        'PyYAML',
        'lxml',
        'jsonpath-rw'
    ],
    # tests_require=['pytest'],
    entry_points=dict(
        console_scripts=['tmpld = tmpld.cli.main:main']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        # 'Topic :: System :: Clustering',
    ]
)

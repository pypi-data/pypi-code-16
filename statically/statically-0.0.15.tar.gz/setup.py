import sys

if sys.version_info.major < 3:
    print("Please use python3")
    sys.exit()

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    readme = open('README.md').read()

from distutils.core import setup
setup(
    name='statically',
    version='0.0.15',
    description='Static site generator',
    long_description = readme,
    url='https://github.com/joajfreitas/statically',
    download_url = 'https://github.com/joajfreitas/statically/tarball/0.0.3',
    author="joajfreitas",
    author_email="joaj.freitas@gmail.com",
    license='GPLv3',
    packages = ['statically', 'statically/logic', 'statically/config'],
    install_requires = [
        'markdown>=2.6',
        'pygments',
        'py-gfm>=0.1.3',
        'pyembed-markdown',
        'Jinja2>=2.9',
        'argparse',
        'pyyaml',
        'requests',
        'pathlib',
    ],
    scripts=['bin/statica'],
    test_suite='nose.collector',
    tests_require=['nose'],
)

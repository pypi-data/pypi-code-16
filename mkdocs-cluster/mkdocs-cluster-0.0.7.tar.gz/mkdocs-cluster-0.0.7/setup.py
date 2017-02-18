from setuptools import setup, find_packages

VERSION = '0.0.7'

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]

# Fetch external css/js/fonts
import subprocess, os.path, sys
def get_libs():
    print('Fetching external css,js and fonts')
    fold = os.path.dirname(__file__)
    dow = os.path.join(fold, 'do')
    if not os.path.exists(dow):
        print('Not fetching external css,js and fonts (asume already done)')
        return
    try:
        if subprocess.call(['sh', dow, 'shacheck']):
            subprocess.check_call(['sh', dow, 'get_libs'])
    except subprocess.CalledProcessError as err:
        print(err)
        sys.exit(1)

if {'build', 'sdist', 'bdist_wheel'} & set(sys.argv):
    get_libs()


setup(
    name="mkdocs-cluster",
    version=VERSION,
    classifiers=CLASSIFIERS,
    url='https://gitlab.com/kaliko/mkdocs-cluster',
    license='BSD',
    description='Another bootstrap theme for MkDocs',
    author='kaliko jack',
    author_email='kaliko@azylum.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['mkdocs>=0.16.0'],
    entry_points={
        'mkdocs.themes': [
            'cluster = mkdocs_cluster',
        ]
    },
    zip_safe=False
)

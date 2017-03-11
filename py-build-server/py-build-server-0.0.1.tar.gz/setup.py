from setuptools import setup, find_packages

version='0.0.1'
setup(
    name='py-build-server',
    version=version,
    packages=find_packages(),
    license='GPL3',
    url='https://github.com/chestm007/py-build-server',
    download_url='https://github.com/chestm007/py-build-server/archive/{}.tar.gz'.format(version),
    author='chestm007',
    author_email='chestm007@hotmail.com',
    description='My build server i run on my home server to check for git repo tags, and push to pypi',
    entry_points="""
        [console_scripts]
        py-build-server=py_build_server.main:cli
    """,
    requires=[
        'click',
        'gitpython',
        'pyyaml'
    ]
)

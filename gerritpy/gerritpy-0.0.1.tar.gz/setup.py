from setuptools import setup, find_packages

setup(
    name = 'gerritpy',
    version = '0.0.1',
    keywords='gerrit py',
    description = 'a library for gerrit rest api',
    license = 'MIT License',
    url = 'https://github.com/diaojunxian/gerritPython',
    author = 'diaojunxian',
    author_email = 'diaojunxian@huami.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ["requests"],
)
from setuptools import setup
import re
import os


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('data_go')


setup(
    name='api-data-go',
    version=version,
    url='http://www.django-rest-framework.org',
    license='BSD',
    description='Get a list of APIs on www.data.go.kr',
    author='Hyunmin',
    author_email='pointer81@gmail.com',
    install_requires=[],
    zip_safe=False,
)

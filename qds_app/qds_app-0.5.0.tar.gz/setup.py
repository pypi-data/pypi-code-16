import os
import versioneer
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name="qds_app",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Rajat Venkatesh",
    author_email="rvenkatesh@qubole.com",
    description="An egg to add migrations to your project",
    packages=find_packages(),
    scripts=[],
    install_requires=required,
    long_description=read('README.md'),
    url="https://github.com/vrajat/qds_app.git"
)



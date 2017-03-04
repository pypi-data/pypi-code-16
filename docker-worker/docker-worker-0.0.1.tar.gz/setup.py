from setuptools import setup, find_packages

setup(
    name='docker-worker',
    install_requires=['docker_py', 'gym', 'six'],
    version='0.0.1',
      packages=[package for package in find_packages()
                if package.startswith('docker_worker')],
)

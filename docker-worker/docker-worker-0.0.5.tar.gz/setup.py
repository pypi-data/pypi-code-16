from setuptools import setup, find_packages

setup(
    name='docker-worker',
    install_requires=['docker>=2.0.0', 'gym', 'six'],
    version='0.0.5',
      packages=[package for package in find_packages()
                if package.startswith('docker_worker')],
)

from distutils.core import setup
from setuptools import find_packages

setup(name='prpp',
      version='1.8',
      description='Python Polycom RealPresence Rest API wrapper',
      author='Adrien | SharingCloud',
      author_email='sharingcloud-app@sharingcloud.com',
      url='http://www.sharingcloud.com/',
      packages=find_packages(),
      install_requires=[
          'requests',
      ], 
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Topic :: System :: Networking',
      ],
)

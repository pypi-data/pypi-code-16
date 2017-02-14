from setuptools import setup
from ardtools.version import get_package_version_str


def readme():
    with open('DESCRIPTION.rst') as f:
        return f.read()


setup(name='ardtools',
      version=get_package_version_str(),
      description='Tools to control Mac OS X Screen Sharing from the Command \
        Line',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration'
      ],
      keywords='system vnc ARD apple remote desktop screen sharing mac osx',
      url='https://bitbucket.org/apollonia/screen-sharing-restart ',
      author='Erehwon Tools',
      author_email='devops@erehwon.xyz',
      license='New BSD',
      download_url='https://bitbucket.org/apollonia/screen-sharing-restart/\
get/master.tar.gz',
      packages=['ardtools'],
      entry_points={
        'console_scripts': [
            'ardtools = ardtools.cli:main_tool'
        ]
      },
      include_package_data=True,
      zip_safe=False)

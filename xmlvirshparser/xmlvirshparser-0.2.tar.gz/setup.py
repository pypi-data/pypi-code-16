from setuptools import setup

setup(name='xmlvirshparser',
      version='0.2',
      description='Parses virsh dump XML output to OpenStack prettytable form',
      url='http://github.com/',
      author='Vikrant Aggarwal',
      author_email='vaggarwa@redhat.com',
      license='MIT',
      packages=['xmlvirshparser'],
      install_requires=['xmltodict', 'prettytable'],
      platforms=['Linux'],
      package_dir={'xmlvirshparser': 'xmlvirshparser'},
      entry_points={
          'console_scripts': [
              'xmlvirshparser=xmlvirshparser:main',
          ],
      },
)


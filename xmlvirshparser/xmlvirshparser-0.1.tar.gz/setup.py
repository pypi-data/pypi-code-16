from setuptools import setup

setup(name='xmlvirshparser',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/',
      author='Vikrant Aggarwal',
      author_email='vaggarwa@redhat.com',
      license='MIT',
      packages=['xmlvirshparser'],
      install_requires=['python-xmltodict', 'python-prettytable'],
      platforms=['Linux'],
      package_dir={'xmlvirshparser': 'xmlvirshparser'},
      entry_points={
          'console_scripts': [
              'xmlvirshparser=xmlvirshparser:main',
          ],
      },
)


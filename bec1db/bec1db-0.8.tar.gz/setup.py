from setuptools import setup

setup(name='bec1db',
      version='0.8',
      description='The hackiest database reader ever',
      author='biswaroop',
      author_email='mail.biswaroop@gmail.com',
      license='MIT',
      packages=['bec1db'],
      install_requires=[
          'pandas'
      ],
      url='https://github.com/biswaroopmukherjee/bec1db',
      zip_safe=False)

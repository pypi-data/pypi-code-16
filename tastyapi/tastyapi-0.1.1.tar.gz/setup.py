from setuptools import setup

setup(name='tastyapi',
      version='0.1.1',
      description='Python wrapper for Tastynode API',
      url='https://tastynode.com',
      author='sssssss340',
      author_email='viis340@gmail.com',
      packages=['tastyapi'],
      install_requires=[
          'requests',
      ],
      entry_points={
          'console_scripts': [
              'TastyAPI=tastyapi.command_line:main'
          ],
      },
      zip_safe=False)

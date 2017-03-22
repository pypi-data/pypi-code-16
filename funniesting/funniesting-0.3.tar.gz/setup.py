from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='funniesting',
      version='0.3',
      description='The funniest joke in the world',
      long_description=readme(),
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['funniesting'],
      install_requires = [
          'markdown',
      ],
      scripts=['bin/joke-scripts'],
      entry_points = {
          'console_scripts': ['joke_console_script=funniesting.command_line:entrypointprinting'],
      },
      include_package_data=True,
      zip_safe=False)


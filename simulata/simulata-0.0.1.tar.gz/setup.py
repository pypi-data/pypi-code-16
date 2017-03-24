from setuptools import setup

setup(name='simulata',
      version='0.0.1',
      description='Creating simulated datasets',
      url='http://github.com/staeiou/simulata',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      license='MIT',
      packages=['simulata'],
      install_requires=[
          'pandas', 'numpy'],
      zip_safe=False)

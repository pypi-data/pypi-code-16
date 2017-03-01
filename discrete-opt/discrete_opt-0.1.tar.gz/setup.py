
from setuptools import setup

setup(
    name='discrete_opt',
    version='0.1',
    description='Provides methods to minimize scalar and multivariate functions of discrete (integer) variables.',
    url='http://github.com/claudiofahey/discrete_opt',
    author='Claudio Fahey',
    author_email='claudiofahey@gmail.com',
    license='MIT',
    packages=['discrete_opt'],
    install_requires=[
        'numpy',
        'scipy',
      ],
    zip_safe=False,
)

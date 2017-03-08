from setuptools import setup

setup(name='datacompare',
      version='0.1',
      description='Compare 2 datasets returning row status',
      url='https://github.com/marcusrehm/data-compare',
      author='Marcus Rehm',
      author_email='marcus.rehm@gmail.com',
      license='MIT',
      packages=['datacompare'],
      install_requires=[
          'pandas',
      ],
      zip_safe=False)

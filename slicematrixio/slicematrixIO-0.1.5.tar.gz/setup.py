from setuptools import setup

setup(name='slicematrixIO',
      version='0.1.5',
      description='SliceMatrix-IO Python API',
      url='http://www.slicematrix.io',
      author='Hekaton LLC',
      author_email='tynan@slicematrix.com',
      license='MIT',
      packages=['slicematrixIO'],
      install_requires=[
          'numpy>=1',
          'pandas',
          'requests==2.5.3'
      ],
      zip_safe=False)

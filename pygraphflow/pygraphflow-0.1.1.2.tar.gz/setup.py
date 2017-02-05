from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pygraphflow',
      version='0.1.1.2',
      description='A driver for GraphFlow DB',
      long_description='A driver for GraphFlow DB',
      classifiers=[ # to add
      ],
      keywords='', # to add
      url='http://www.graphflow.io/',
      author='GraphFlow Team',
      author_email='amine.mhedhbi@uwaterloo.ca', # graphflow.db@uwaterloo.ca would be nice!
      license='MIT',
      packages=['pygraphflow'],
      install_requires=[
          'grpcio',
      ],
      include_package_data=True,
      zip_safe=False)


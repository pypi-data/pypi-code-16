from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='harvest-invoice',
      version='0.0.1',
      description='Generate invoice using harvest API',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing :: Linguistic',
      ],
      keywords='harvest invoice',
      url='http://github.com/storborg/funniest',
      author='Aldiantoro Nugroho',
      author_email='kriwil@gmail.com',
      license='Apache 2',
      packages=['harvest_invoice'],
      install_requires=[
          'click>=6,<7',
          'requests>=2,<3',
      ],
      entry_points={
          'console_scripts': ['harvest_invoice=harvest_invoice.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)

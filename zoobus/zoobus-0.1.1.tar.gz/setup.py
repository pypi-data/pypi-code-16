import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'thrift',
    'python-dateutil',
    'pytz',
    ]

setup(name='zoobus',
      version='0.1.1',
      description="Vincent Wen's Personal Common Packages",
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python",
      ],
      url='https://github.com/vincentwyshan/ZooBus',
      author='Vincent Wen',
      author_email='vincent.wyshan@gmail.com',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      #test_suite='',
      install_requires=requires,
      entry_points={
      }
)


from setuptools import setup, find_packages
import os
import vsscli


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='vsscli',
      version=vsscli.__version__,
      description='EIS Virtual Cloud Command Line Interface',
      author='University of Toronto',
      author_email='jm.lopez@utoronto.ca',
      url='https://gitlab.eis.utoronto.ca/vss/vsscli',
      install_requires=required,
      packages=find_packages(),
      package_dir={'vsscli': 'vsscli'},
      include_package_data=True,
      package_data={'vsscli': ['config/*']},
      entry_points='''
        [console_scripts]
        vss=vsscli.cli:cli
        ''',
      license='MIT License',
      long_description=read('README.rst'),
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Development Status :: 4 - Beta",
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      platforms=['Linux', 'Solaris', 'Mac OS-X', 'Unix'],
      zip_safe=False
      )

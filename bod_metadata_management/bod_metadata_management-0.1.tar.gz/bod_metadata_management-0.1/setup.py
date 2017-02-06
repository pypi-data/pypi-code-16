from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='bod_metadata_management',
      version='0.1',
      description='modules, libraries, and scripts to manage metadata for Boston Open Data',
      long_description=readme(),
      url='https://github.com/vmanamino/bod_metadata_management',
      author='Viral Amin',
      author_email='vmanamino@gmail.com',
      license='MIT',
      packages=['bod_metadata_management'],
      install_requires=['slugify',],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      scripts=['bin/*'],
      include_package_data=True,
      zip_safe=False)
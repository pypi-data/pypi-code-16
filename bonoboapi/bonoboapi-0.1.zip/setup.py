from setuptools import setup, find_packages

setup(name='bonoboapi',
      version='0.1',
      description='bonobo API for sending messages to Bonobo.ai',
      url='',
      author='bonobo',
      author_email='ohad@bonobo.ai',
      license='?',
      packages= find_packages(exclude=['contrib', 'docs', 'tests*']),
      zip_safe=False,
      classifiers = [
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'],
      install_requires=['requests']
)
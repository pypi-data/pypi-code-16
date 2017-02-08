from setuptools import setup

setup(name='sve_common_tools',
      version='0.1.6.71',
      author='Riccardo Russo',
      author_email='riccardo.russo79@gmail.com',
      description='Utility pack per progetti sve',
      long_description=open('README.rst').read(),
      url='https://pypi.python.org/pypi/sve_common_tools',
      license='MIT',
      packages=['sve_common_tools'],
      zip_safe=False,
      install_requires=['paramiko>=1.10.0']
      )

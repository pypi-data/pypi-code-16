from setuptools import setup
# https://python-packaging.readthedocs.io/en/latest/minimal.html
# python setup.py sdist upload
def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='nodewire',
      version='0.4.3',
      description='NodeWire Gateway',
      long_description=readme(),
      url='http://www.nodewire.org',
      author='Ahmad Sadiq',
      author_email='sadiq.a.ahmad@gmail.com',
      license='BSD',
      packages=['nodewire'],
      scripts=['bin/nodewiregw.py', 'bin/nw_gateway.py'],
      install_requires=[
            'paho-mqtt',   # no longer needed
            'configparser',
            'netifaces', # no longer needed
            'pyserial',
            'requests'
      ],
      zip_safe=False)

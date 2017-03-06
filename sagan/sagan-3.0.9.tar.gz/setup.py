from distutils.core import setup

setup(
    name='sagan',
    version='3.0.9',
    packages=['sagan'],
    install_requires=["smbus-cffi", "RPIO"],
    url='',
    license='',
    author='T A H Smith, A W Collins',
    author_email='sagan@cuberider.com',
    description='Python library for interfacing with sagan board'
)

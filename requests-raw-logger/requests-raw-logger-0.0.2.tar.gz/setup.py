from distutils.core import setup

setup(
    name='requests-raw-logger',
    version='0.0.2',
    packages=['requests_raw_logger'],
    url='https://github.com/yozel/requests-raw-logger',
    license='MIT',
    author='yozel',
    author_email='me@yozel.co',
    description='A request and response logger for requests',
    install_requires=['requests']
)

from distutils.core import setup

setup(
    name='devip',
    packages=['devip', 'devip.services'],
    version='0.1.9',
    description='CLI that updates your public IP address in external services you use and depend on IP-authentication.',
    author='Phivos Stylianides',
    author_email='stphivos@gmail.com',
    url='https://github.com/stphivos/devip',
    keywords=['ip-authentication', 'aws'],
    classifiers=[],
    install_requires=['boto3>=1.4.1'],
    entry_points={'console_scripts': ['devip = devip.__main__:run', ], },
)

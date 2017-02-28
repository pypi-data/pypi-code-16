from setuptools import setup

setup(
    name='lastpass-cloudbleed',
    version='1.0',
    url='https://github.com/angstwad/lastpass-cloudbleed',
    license='Apache 2.0',
    author='Paul Durivage',
    author_email='pauldurivage@gmail.com',
    description='Compares the publicly available CloudFlare domains list to your LastPass vault, listing potentially compromised domains in your vault.',
    install_requires=[
        'requests',
        'urltools>=0.3.2',
        'lastpass-python>=0.1.1',
    ],
    packages=['lastpass_cloudbleed'],
    entry_points={
        'console_scripts': [
            'lastpass-cloudbleed=lastpass_cloudbleed:main'
        ]
    }
)

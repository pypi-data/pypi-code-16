from setuptools import find_packages, setup


setup(
    name = 'bucket-list',
    packages = find_packages(),
    version = '0.3.6',
    description = 'Command line interface for managining bucketlist',
    author = 'Arpit Bhayani',
    author_email = 'arpit.b.bhayani@gmail.com',
    url = 'https://github.com/arpitbbhayani/bucket-list',
    download_url = 'https://github.com/arpitbbhayani/bucket-list',
    keywords = ['bucket list', 'cli'],
    include_package_data=True,
    entry_points= {
        'console_scripts': [
            'bucket-list=bucketlist.cmdline:execute'
        ]
    },
    install_requires=[
        'speedyio==0.4',
        'requests==2.12.4',
        'terminaltables==3.1.0'
    ]
)

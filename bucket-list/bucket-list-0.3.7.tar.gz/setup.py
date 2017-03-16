from setuptools import find_packages, setup


setup(
    name = 'bucket-list',
    packages = find_packages(),
    version = '0.3.7',
    description = 'A beautiful command line tool to manage your todos and bucket lists',
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
        'jsoncache==0.0.3',
        'timecheck==0.0.2',
    ]
)

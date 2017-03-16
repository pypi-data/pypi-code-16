from setuptools import find_packages, setup


setup(
    name = 'timecheck',
    packages = find_packages(),
    version = '0.0.2',
    description = 'Easy and efficient way to gather time metrics for Python functions',
    author = 'Arpit Bhayani',
    author_email = 'arpit.b.bhayani@gmail.com',
    url = 'https://github.com/arpitbbhayani/timecheck',
    download_url = 'https://github.com/arpitbbhayani/timecheck',
    keywords = ['time', 'metrics'],
    include_package_data=True,
    install_requires=[
        'numpy==1.12.0',
        'matplotlib==2.0.0'
    ],
    entry_points= {
        'console_scripts': [
            'timecheck=timecheck.cmdline:execute'
        ]
    }
)

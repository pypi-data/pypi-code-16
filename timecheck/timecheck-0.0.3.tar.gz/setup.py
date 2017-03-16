from setuptools import find_packages, setup


setup(
    name = 'timecheck',
    packages = find_packages(),
    version = '0.0.3',
    description = 'Easy and efficient way to gather time metrics for Python functions',
    author = 'Arpit Bhayani',
    author_email = 'arpit.b.bhayani@gmail.com',
    url = 'https://github.com/arpitbbhayani/timecheck',
    download_url = 'https://github.com/arpitbbhayani/timecheck',
    keywords = ['time', 'metrics'],
    include_package_data=True,
    install_requires=[]
)

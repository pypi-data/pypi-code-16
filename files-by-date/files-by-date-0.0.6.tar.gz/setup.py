from setuptools import setup, find_packages

from files_by_date.utils.version import get_version

setup(
    name='files-by-date',
    packages=find_packages(),
    version=get_version(),
    description='Moves files from one directory into another grouping by created month',
    author='Justin Beall',
    author_email='jus.beall@gmail.com',
    url='https://github.com/DEV3L/python-files-by-date',
    download_url='https://github.com/DEV3L/python-files-by-date/tarball/{version}'.format(version=get_version()),
    keywords=['dev3l', 'file management'],  # arbitrary keywords
    install_requires=[
        'pytest==3.0.6',
        'coverage==4.3.4',
        'bandit==1.4.0'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'files-by-date=files_by_date.app.run:run'
        ]},
)

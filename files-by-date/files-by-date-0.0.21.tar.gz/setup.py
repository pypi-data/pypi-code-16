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
        'bandit==1.4.0',
        'pylint==1.6.5',
        'tox==2.6.0',
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'files-by-date=files_by_date.app.run:run'
        ]},
)

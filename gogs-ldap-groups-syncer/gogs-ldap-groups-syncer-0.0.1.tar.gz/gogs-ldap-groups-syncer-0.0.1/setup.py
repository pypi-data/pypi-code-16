from setuptools import setup, find_packages

version = "0.0.1"

long_description = ""
try:
    long_description = file('README.md').read()
except Exception:
    pass

license = ""
try:
    license = file('LICENSE').read()
except Exception:
    pass


setup(
    name='gogs-ldap-groups-syncer',
    version=version,
    description='A Gogs LDAP groups syncer',
    author='Pablo Saavedra',
    author_email='saavedra.pablo@gmail.com',
    url='http://github.com/psaavedra/gogs-ldap-groups-syncer',
    packages=find_packages(),
    package_data={
    },
    scripts=[
        "tools/gogs-ldap-groups-syncer",
    ],
    zip_safe=False,
    install_requires=[
        "psycopg2",
        "python-ldap",
    ],
    data_files=[
        ('/usr/share/doc/gogs-ldap-groups-syncer/',
            ['cfg/gogs-ldap-groups-syncer.cfg.example']),
    ],

    download_url='https://github.com/psaavedra/gogs-ldap-groups-syncer/zipball/master',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    long_description=long_description,
    license=license,
    keywords="python gogs syncer ldap",
)

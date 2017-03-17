from setuptools import setup, find_packages
from helga_pointing_poker import __version__ as version


setup(
    name="helga-pointing-poker",
    version=version,
    description=('Pointing poker for helga'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
    keywords='irc bot pointing-poker',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=['helga', 'requests'],
    test_suite='tests/test_pointing_poker',
    entry_points=dict(
        helga_plugins=[
            'pointing-poker = helga_pointing_poker.helga_pointing_poker:pointing_poker',
        ],
    ),
)

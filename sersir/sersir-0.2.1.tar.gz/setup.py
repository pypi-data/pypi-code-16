from setuptools import setup, find_packages

setup(
    name='sersir',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'RPi.GPIO',
    ],
    extras_require={
        'systemd': ['systemd'],
    },
    use_scm_version={
        'root': '..',
        'relative_to': __file__,
    },
    setup_requires=['pytest-runner', 'setuptools_scm'],
    tests_require=[
        'pytest'
    ],
    zip_safe=True,

    maintainer="Christian Kohlstedde",
    maintainer_email="christian.kohlstedde@ic-consult.de",

    keywords="Raspberry Pi gpio jenkins",
    description="server siren - failed jenkins job activates a gpio pin / siren",
    url="https://bitbucket.org/icconsult/sersir",

    license="MIT",

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
    ],
)

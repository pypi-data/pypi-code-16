from setuptools import find_packages, setup


dependencies = open('requirements.txt').read().splitlines()

setup(
    name='pyaxmlparser',
    version='0.1.3',
    url='https://github.com/appknox/pyaxmlparser',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    package_data={
        '': ['*.txt'],
    },
    py_modules=['pyaxmlparser'],
    entry_points='',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

from setuptools import find_packages, setup

package = 'cfm'
version = '0.2'

setup(
    name=package,
    version=version,
    description="Config file manager in Python 3",
    url='https://www.github.com/solkaz/cfm',

    author='Jeff Held',
    author_email='jheld135@gmail.com',

    license='MIT',

    packages=find_packages('cfm'),

    entry_points={
        'console_scripts': [
            'cfm=cfm:main',
        ],
    },
)

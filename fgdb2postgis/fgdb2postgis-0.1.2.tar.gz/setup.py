
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='fgdb2postgis',
    version='0.1.2',
    description="""File geodatabase to postgis convertor""",
    long_description=open('README.rst').read(),
    author='George Ioannou',
    author_email='gmioannou@cartologic.com',
    url='https://github.com/cartologic/fgdb2postgis',
    packages=[
        'fgdb2postgis',
    ],
    package_data={'fgdb2postgis': ['sql_files/*.sql']},
    include_package_data=True,
    install_requires=['numpy', 'psycopg2', 'pyyaml'],
    license="MIT",
    zip_safe=False,
    platform="Windows",
    keywords='fgdb2postgis',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'console_scripts': [
            'fgdb2postgis = fgdb2postgis.__main__:main',
        ],
    },
)

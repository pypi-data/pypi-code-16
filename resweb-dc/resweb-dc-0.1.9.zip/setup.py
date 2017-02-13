from setuptools import setup, find_packages
version = __import__('resweb').__version__
setup(
    name='resweb-dc',
    version=version,
    description='Pyres web interface',
    author='dc',
    author_email='loooseleaves@gmail.com',
    maintainer='dc',
    license='MIT',
    url='https://github.com/dawncold/resweb',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data={'resweb': ['templates/*.mustache', 'static/*']},
    install_requires=[
        'pyres>=1.3',
        'flask'
    ],
    entry_points="""\
    [console_scripts]
    resweb=resweb.core:main
    """,
    classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python'],
)

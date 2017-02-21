from setuptools import setup
setup(
    name='cetup',
    packages=['cetup'],
    version='0.1',
    description='Quick setup tool for C and C++ projects',
    author='Sixten Hilborn',
    author_email='sixten.hilborn@gmail.com',
    url='https://github.com/sixten-hilborn/cetup',
    download_url='https://github.com/sixten-hilborn/cetup/tarball/0.1',
    keywords=['C', 'C++'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python'
    ],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cetup=cetup.cetup:main',
        ],
    },
)

from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name="quilt",
    version="2.0.1",
    packages=find_packages(),
    description='Quilt is an open-source data frame registry',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    author='quiltdata',
    author_email='founders@quiltdata.io',
    license='LICENSE',
    url='https://github.com/quiltdata/quilt',
    download_url='https://github.com/quiltdata/quilt/releases/tag/v2.0.0-alpha',
    keywords='quilt quiltdata shareable data dataframe package platform pandas',
    install_requires=[
        'appdirs>=1.4.0',
        'future>=0.16.0',
        'pandas>=0.19.2',
        'pyOpenSSL>=16.2.0',
        'pyyaml>=3.12',
        'requests>=2.12.4',
        'responses>=0.5.1',
        'tables>=3.3.0',
        'xlrd>=1.0.0',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['quilt=quilt.tools.command:main'],
    }
)

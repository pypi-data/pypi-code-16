from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='npp_dotmanager',
    version='0.2.0',
    description='N+1th dotmanager manager with public and private repository and git support',
    long_description=readme(),
    url='https://github.com/sxnwlfkk/dotmanager',
    author='Saxon Wolfkok',
    author_email='saxonwolfkok@gmail.com',
    license='GPL',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="configuration setuptools dotmanager linux unix",
    packages=["dotmanager"],
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": ["dotmanager=dotmanager.dotmanager:main"],
    },
    zip_safe=False,
    include_package_data=True,
)
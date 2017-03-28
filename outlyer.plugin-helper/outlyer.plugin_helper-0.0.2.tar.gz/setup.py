from setuptools import setup


setup(
    name='outlyer.plugin_helper',
    description = 'Outlyer plugin helper',
    version='0.0.2',
    license='MIT',
    url='https://github.com/outlyerapp/plugin_helper',
    download_url='https://github.com/outlyerapp/plugin_helper/archive/0.1.tar.gz',

    author='Colin Hemmings',
    author_email='colin.hemmings@outlyer.com',
    keywords=['outlyer', 'plugin', 'helper'],

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'docker==2.2.0',
        'requests==2.12.4'
    ],
    packages=[
        'outlyer',
        'outlyer.plugin_helper',
        'outlyer.plugin_helper.container'
    ],
)
if __name__ == "__main__":
    pass
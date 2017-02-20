from setuptools import setup

setup(
    name="cfgen",
    version="0.2.5",
    description="Configuration tool for configuration files",
    author="Renat Zhilkibaev",
    author_email="rzhilkibaev@gmail.com",
    license="MIT",
    url="https://github.com/rzhilkibaev/cfgen",
    packages=["cfgen"],
    install_requires=["docopt", "future", "jinja2"],
    scripts=["bin/cfgen"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        ],
)

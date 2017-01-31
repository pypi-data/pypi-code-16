from setuptools import setup, find_packages
import os

HERE = os.path.abspath(os.path.dirname(__file__))
def get_long_description():
    dirs = [ HERE ]
    if os.getenv("TRAVIS"):
        dirs.append(os.getenv("TRAVIS_BUILD_DIR"))

    long_description = ""

    for d in dirs:
        rst_readme = os.path.join(d, "README.rst")
        if not os.path.exists(rst_readme):
            continue

        with open(rst_readme) as fp:
            long_description = fp.read()
            return long_description

    return long_description

long_description = get_long_description()

version='0.1.1'
setup(
    name="peoplegraph-api-client",
    version=version,
    description="Peoplegraph api client",
    long_description=long_description,
    keywords="peoplegraph",
    author="Deep Compute, LLC",
    author_email="contact@deepcompute.com",
    url="https://github.com/deep-compute/peoplegraph-api-client",
    download_url="https://github.com/deep-compute/peoplegraph-api-client/tarball/%s" % version,
    license='MIT License',
    packages=["peoplegraph_api_client"],
    install_requires=[
        "python-dateutil",
        "requests>=2.11",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "peoplegraph = peoplegraph_api_client.main:main",
        ]
    }
)

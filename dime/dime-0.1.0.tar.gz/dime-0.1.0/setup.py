from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

project_url = "https://github.com/"
project_url += "lepisma/dime"

setup(
    name="dime",
    version="0.1.0",
    description="Virtual Desktop time tracker",
    long_description=readme,
    author="Abhinav Tushar",
    author_email="abhinav.tushar.vs@gmail.com",
    url=project_url,
    install_requires=["hy"],
    scripts=["dime"],
    classifiers=(
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only"
    ))

#!/usr/bin/python3

from distutils.core import setup

setup(name="unleash_potential",
      version="0.8",
      description="Unleash your potential with System76!",
      author="Ryan Sipes",
      author_email="ryan@system76.com",
      url="https://system76.com",
      packages=["unleash_potential"],
      install_requires=["asciimatics"],
      scripts=["unleash_potential/unleash-potential"],
      package_data={"unleash_potential" : ["assets/*"], }
     )

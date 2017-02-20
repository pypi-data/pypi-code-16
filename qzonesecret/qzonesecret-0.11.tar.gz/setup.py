from setuptools import setup, find_packages
setup(
      name="qzonesecret",
      version="0.11",
      description="Find QZone Secrets",
      author="Charles Yang",
	  author_email="mryang@minelandcn.com",
      url="https://mryang.minelandcn.com",
      license="LGPL",
      packages= find_packages(),
      scripts=["qzonesecret/SecretGet.py"],
      )

from setuptools import setup, find_packages
setup(
      name="qzonesecret",
      version="0.12",
      description="Find QZone Secrets",
      author="Charles Yang",
	  author_email="mryang@minelandcn.com",
      url="https://mryang.minelandcn.com",
      license="LGPL",
      packages= find_packages(),
      scripts=["SecretGet.py"],
      )

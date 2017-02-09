from setuptools import setup

setup(
      name="pyrstructs",
      version="0.1",
      description="Python data structures backed by Redis",
      author="merlin83",
      license="BSD",

      packages=["rstructs"],

      install_requires=["redis>=2.7.0"],
      setup_requires=["nose"],
      tests_require=["coverage"],

      include_package_data=True,
)
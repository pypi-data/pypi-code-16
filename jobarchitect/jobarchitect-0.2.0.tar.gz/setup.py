from setuptools import setup

version = "0.2.0"
readme = open('README.rst').read()
url = "https://github.com/JIC-CSB/jobarchitect"

setup(name="jobarchitect",
      packages=["jobarchitect"],
      version=version,
      description="Tools for batching jobs and dealing with file paths",
      long_description=readme,
      include_package_data=True,
      author='Tjelvar Olsson',
      author_email='tjelvar.olsson@jic.ac.uk',
      url=url,
      install_requires=["dtool"],
      entry_points={
          'console_scripts': ['_analyse_by_ids=jobarchitect.agent:cli',
                              'sketchjob=jobarchitect.sketchjob:cli']
      },
      download_url="{}/tarball/{}".format(url, version),
      license="MIT")

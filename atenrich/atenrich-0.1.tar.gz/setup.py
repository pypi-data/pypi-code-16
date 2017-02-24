from setuptools import setup

setup(
      name="atenrich",
      version="0.1",
      packages=['atenrich'],
      package_data={'atenrich': ['data/db/GeneListDB.db','data/config/db_config.json']},
      install_requires=['Click','numpy','scipy','pandas'],
      scripts=['bin/atenrich'],
)
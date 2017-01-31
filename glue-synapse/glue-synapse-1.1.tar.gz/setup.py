from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
cluster=glue_synapse.cluster:setup"""

setup(name='glue-synapse',
      version='1.1',
      description='Synapse localization clustering and analysis for Glue. Uses DBSCAN clustering algorithm to group channels and display centroid distances.',
      url='http://www.thesettleproject.com',
      author='Brett Settle',
      author_email='brettjsettle@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={'': ['cluster_ui.ui']},
      include_package_data=True,
      install_requires=["glueviz>=0.9", 'glue-vispy-viewers', 'sklearn'],
      entry_points=entry_points,
      zip_safe=False)
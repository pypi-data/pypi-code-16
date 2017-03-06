from setuptools import setup, find_packages
import sys, os

version = '0.2.3'

setup(name='family',
      version=version,
      description="Easy to create your microservice based on multiple python frameworks.",
      long_description="""\
""",
      keywords='microservice falcon flask',
      author='torpedoallen',
      author_email='torpedoallen@gmail.com',
      url='https://github.com/daixm/family',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click',
          'PasteScript',
          'check-manifest',
          'aliyuncli',
          'aliyun-python-sdk-slb',
          'django',
          'wheel',
      ],
      entry_points="""
      [console_scripts]
      family-createapp=family.commands.createapp:create
      family-aliyun-init=family.commands.aliyun:init_listener
      family-aliyun-deploy=family.commands.aliyun:deploy
      [paste.paster_create_template]
      falcon = family.templates.basic:FalconTemplate
      flask = family.templates.basic:FlaskTemplate
      """,
      )

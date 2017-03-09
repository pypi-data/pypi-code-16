__author__ = 'creeper'
# import ez_setup
# ez_setup.use_setuptools()
from setuptools import setup,find_packages

setup(
    url=' ', 
    name = 'django_analysis_tool',
    version = '1.1.20',
    description= 'Tools to analysis lab task',
    author = "creeper",
    author_email = 'creeper@163.com',
    packages = find_packages(),
    package_dir = {'': '.'},
    package_data = {"":["./db.sqlite3",
                        "./manage.py",
                        "./run.py",
                        "./lab_analysis_tools/templates/lab_analysis_tools/*",
                        "./lab/instrumentation_json/*",
                        "./lab/static/index/css/*",
                        "./lab/static/index/fonts/*",
                        "./lab/static/index/img/*",
                        "./lab/static/index/js/*",
                        "./lab/static/task_all/css/*",
                        "./lab/static/task_all/fonts/*",
                        "./lab/static/task_all/js/*",
                        "./lab/static/zip/css/*",
                        "./lab/static/zip/fonts/*",
                        "./lab/static/zip/js/*",
                        "./lab/static/wait/_css/*",
                        "./lab/static/wait/_scripts/*"
                        ]},
    scripts=["scripts/run.py"],
    install_requires=[
        'Django==1.9.4',
        'threadpool==1.3.2',
      ],
    include_package_data = True
)

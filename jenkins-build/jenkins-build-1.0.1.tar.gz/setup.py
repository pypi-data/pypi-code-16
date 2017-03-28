from setuptools import setup

setup(name='jenkins-build',
      version=open('version').read().strip(),
      description='A python tool to manage(trigger/query/cancel/stop/log) jenkins build',
      long_description='support to trigger a jenkins build with/without parameters in configure file, query a build status with queueid or build number, cancel a build with queueid or build number, get the build log with queueid or build number with option to save the log output to a log file ',
      keywords='jenkins build trigger cancel stop query log queue_id build_number',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Build Tools',
      ],
      url='https://github.com/LeEco-SEE/jenkins-build',
      author='Huaqiang Li',
      author_email='lihuaqiang@le.com',
      license='Apache License, Version 2.0',
      packages=['jenkins_build'],
      platforms = "any",
      install_requires = [
          'python-jenkins',
      ],
      entry_points={
          'console_scripts': ['jenkins-build=jenkins_build.jenkins_build:main'],
      },
      include_package_data=True,
      zip_safe=False)

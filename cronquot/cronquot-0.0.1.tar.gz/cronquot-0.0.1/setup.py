from setuptools import setup#, find_packages

long_desc = ''
with open('README.md') as f:
    logn_desc = f.read()

setup(name='cronquot',
      version='0.0.1',
      description='Cron scheduler.',
      long_description=long_desc,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
      keywords='cron crontab schedule',
      author='Shohei Mukai',
      author_email='xxxx@mail.mail',
      url='http://www.www',
      license='MIT',
      # packages=find_packages,
      entry_points={
          'console_scripts': [
              'cronquot = cronquot.cronquot:execute_from_console'],
          },
      install_requires=['crontab']
      )

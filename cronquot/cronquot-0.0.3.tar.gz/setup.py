from setuptools import setup

long_desc = ''
with open('README.txt') as f:
    logn_desc = f.read()

setup(name='cronquot',
      version='0.0.3',
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
      author_email='mukaishohei76@gmail.com',
      url='https://github.com/pyohei/cronquot',
      license='MIT',
      packages=['cronquot'],
      entry_points={
          'console_scripts': [
              'cronquot = cronquot.cronquot:execute_from_console'],
          },
      install_requires=['crontab']
      )

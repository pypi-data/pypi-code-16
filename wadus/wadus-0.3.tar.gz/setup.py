from setuptools import setup

setup(name='wadus',
      version='0.3',
      description='Cloud basic tool',
      keywords='wadus DevOps sysadmin cloud aws',
      url='http://github.com/jesus-sayar/wadus',
      author='Jesus Sayar',
      author_email='sayar.jesus@gmail.com',
      license='MIT',
      scripts=['bin/wadus'],
      packages=['wadus'],
      install_requires=[
          'boto3',
          'terminaltables'
      ],
      include_package_data=True,
      zip_safe=False)

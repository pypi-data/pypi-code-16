from setuptools import setup

setup(name='dai',
      version='0.3.75',
      description='python worker for distributedAI',
      url='http://github.com/oeway/distributedAI',
      author='Wei OUYANG',
      author_email='wei.ouyang@cri-paris.org',
      license='MIT',
      packages=['dai'],
      install_requires=[
          'python-ddp',
          'sh'
      ],
      zip_safe=False)

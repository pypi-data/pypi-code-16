from setuptools import setup

setup(name='django-request-logger',
      version='0.1.1',
      description='Django middleware that logs http request information to database.',
      url='https://git.pispalanit.fi/pit/django-request-logger',
      author='Joni Saarinen',
      author_email='joni.saarinen@pispalanit.fi',
      license='MIT',
      packages=['request_logger'],
      install_requires=[
          'Django',
      ],
zip_safe=False)

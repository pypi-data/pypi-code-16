from distutils.core import setup
setup(
  name='fluentmetrics',
  packages=['fluentmetrics'],
  version='0.1.5',
  description='Fluent AWS Metrics Logging',
  author='Troy Larson',
  author_email='troylar@gmail.com',
  url='https://github.com/troylar/FluentMetrics',
  download_url='https://github.com/troylar/FluentMetrics/tarball/0.1',
  keywords=['metrics', 'logging', 'aws'],
  install_requires=['arrow', 'boto3'],
  classifiers=[],
)

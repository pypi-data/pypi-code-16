from distutils.core import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='xyaml',
    version='1.0.2',
    packages=[''],
    url='https://github.com/bsimpson888/xyaml',
    license='GPL',
    author='Marco Bartel',
    author_email='bsimpson888@gmail.com',
    description='xyaml is a extension to PyYAML which allows you to include child yaml files.',
    install_requires=requirements,
    data_files=[('', ['requirements.txt'])]
)

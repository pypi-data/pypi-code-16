from distutils.core import setup

setup(
    name='polygonizer',
    packages=['polygonizer'],  # this must be the same as the name above
    version='0.1',
    description='A tool to pull down imagery from gbdx more systematically',
    author='Mahmoud Lababidi',
    author_email='lababidi+py@gmail.com',
    url='https://github.com/DigitalGlobe/polygonizer',  # use the URL to the github repo
    download_url='https://github.com/DigitalGlobe/polygonizer/archive/0.1.tar.gz',  # I'll explain this in a second
    keywords=['gbdx', 'imagery', 'satellite'],  # arbitrary keywords
    requires=['fiona', 'requests', 'shapely', 'numpy', 'gbdxtools'],
    classifiers=[],
)

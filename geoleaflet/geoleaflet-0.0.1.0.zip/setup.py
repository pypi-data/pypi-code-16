from setuptools import setup

setup(
    name             = 'geoleaflet',
    version          = '0.0.1.0',
    packages         = ['geoleaflet',],
    install_requires = ['geojson',],
    license          = 'MIT License',
	url              = 'https://github.com/Data-Mechanics/geoleaflet',
	author           = 'Andrei Lapets',
	author_email     = 'a@lapets.io',
    description      = 'Python library to quickly build a standalone HTML file with a Leaflet visualization of a GeoJSON object.',
    long_description = open('README').read(),
)

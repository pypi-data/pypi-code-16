from distutils.core import setup
import os

# version (shape.function.path)
# python setup.py sdist upload
setup(
	name='django-trigger',
	version='1.0.1',
	packages=['trigger'],
	url='https://github.com/luismoralesp/trigger',
	author="Luis Miguel Morales Pajaro",
	author_email="luismiguel.mopa@gmail.com",
	licence="Creative Common",
	description="bese django trigger",
	platform="Linux",
	zip_safe=False,
	include_package_data=True,
)
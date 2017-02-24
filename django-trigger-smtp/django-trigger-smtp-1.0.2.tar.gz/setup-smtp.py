from distutils.core import setup
import os

# version (shape.function.path)
# python setup.py sdist upload
setup(
	name='django-trigger-smtp',
	version='1.0.2',
	packages=['smtp'],
	url='https://github.com/luismoralesp/trigger',
	author="Luis Miguel Morales Pajaro",
	author_email="luismiguel.mopa@gmail.com",
	licence="Creative Common",
	description="bese django trigger, smtp plugin",
	platform="Linux",
	zip_safe=False,
	include_package_data=True,
)
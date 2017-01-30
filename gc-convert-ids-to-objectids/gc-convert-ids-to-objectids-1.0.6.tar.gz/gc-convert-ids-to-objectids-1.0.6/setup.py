from setuptools import setup, Extension

setup(
    name='gc-convert-ids-to-objectids',
    version='1.0.6',
    author='Alex Etling',
    author_email='alex@gc.com',
    packages=['convert_ids'],
    package_dir={'': '.'},
    zip_safe=False,
    url='https://github.com/gamechanger/cython-extensions/tree/master/convert_ids_to_objectids',
    ext_modules = [Extension("convert_ids/convert_ids_to_objectids", ["convert_ids/convert_ids_to_objectids.c"])]
)
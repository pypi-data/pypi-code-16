try:
  from setuptools import setup, Extension
except ImportError:
  from distutils.core import setup, Extension
import os.path
import re

extmod = Extension('sjts',
                    sources = ['./python/ujson.c',
                               './python/objToJSON.c',
                               './python/JSONtoObj.c',
                               './lib/ultrajsonenc.c',
                               './lib/ultrajsondec.c'],
                    include_dirs = ['./python', './lib'],
                    extra_compile_args=['-D_GNU_SOURCE'])

def get_version():
    filename = os.path.join(os.path.dirname(__file__), './python/version.h')
    file = None
    try:
        file = open(filename)
        header = file.read()
    finally:
        if file:
            file.close()
    m = re.search(r'#define\s+UJSON_VERSION\s+"(\d+\.\d+(?:\.\d+)?)"', header)
    assert m, "version.h must contain UJSON_VERSION macro"
    return m.group(1)

f = open('README.rst')
try:
    README = f.read()
finally:
    f.close()

setup(name='shooju-ts',
      version=get_version(),
      description="Shooju Time Series (SJTS) Serializer",
      long_description=README,
      ext_modules = [extmod],
      keywords='data, client, shooju',
      author='Shooju, LLC',
      author_email='support@shooju.com',
      url='http://shooju.com',
      license='TBD',
      platforms=['any'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[]
)

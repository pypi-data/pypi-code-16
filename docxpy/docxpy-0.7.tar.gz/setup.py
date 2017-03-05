import glob
from distutils.core import setup
from pydocx import VERSION

# get all of the scripts
scripts = glob.glob('bin/*')

setup(
  name='docxpy',
  packages=['docxpy'],
  version=VERSION,
  description='A pure python-based utility to extract text, hyperlinks and images'
              'from docx files.',
  author='Ankush Shah, Yalei Du',
  author_email='yaleidu@163.com',
  url='https://github.com/badbye/python-docx2txt',
  keywords=['python', 'docx', 'text', 'links', 'images', 'extract'],
  scripts=scripts,
  test_suite='nose.collector',
  tests_require=['nose'],
  classifiers=[],
)

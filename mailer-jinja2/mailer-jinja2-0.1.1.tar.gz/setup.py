from distutils.core import setup

setup(
    name='mailer-jinja2',
    packages=['mailer_jinja2'],  # this must be the same as the name above
    version='0.1.1',
    description='A Python 3 mailer package with Jinja2 template',
    author='Theo Bouwman',
    author_email='theobouwman98@gmail.com',
    url='https://github.com/theobouwman/mailer-jinja2',  # use the URL to the github repo
    keywords=['mail', 'template', 'jinja2'],  # arbitrary keywords
    classifiers=[],
    package_dir= {'': 'src'},
    install_requires=['Jinja2>=2.9,<3'],
)

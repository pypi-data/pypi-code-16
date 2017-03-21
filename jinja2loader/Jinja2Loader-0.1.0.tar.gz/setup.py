from setuptools import setup


__doc__ = """
jinja2loader
============

This package is to be used with simple cherrypy applications needing a quick
and easy way to load templates from the file system.

Importing and Setup
-------------------
In order to use this module correctly you must import it and then set the
`template_directory`. The `template_directory` is initially set to be
`os.path.join(os.getcwd(), 'templates')`.

If your templates are stored in './templates/' then you can just import this
module. ::
    
    import jinja2loader

However, if your templates are in another directory structure you will
need to import the module and then set the template `template_directory`. A
helper function has been create to allow this, you can use it via calling
`jinja2loader.set_template_directory('template_directory')`. ::
    
    import jinja2loader
    jinja2loader.set_template_directory('../resources/templates')


load_template
-------------
This Function wraps an application method which returns the
context for a template, this decorator takes a single arguement, which is
the `template_name` to pass to `Environment.get_template(template_name)`
When using this decorator all you need to do from your application
function is to return the context you want to pass into the template. In
addition you need to specify the `template_name` as the argument to the
decorator like `@load_template('template_name.html')`
See example below which loads a template 'test.html' using
`Environment.get_template(template_name)`. ::

    class Application(object):
        @cherrypy.expose
        @load_template('test.html')
        def index(self):
            context = {'name': 'derp',
                       'name_list': ['bleep',
                                     'blerp',
                                     'herp']}
            return context

The above example will result in the template 'test.html' being rendered
with the context from the function `Application.index()`
If nothing is passed in as the context like in the below example, the
decorator method will automatically replace this with an empty `Dict`
before the call the render. ::

    @load_template('test.html')
    def index(self):
        return

The above example will return the 'test.html' template, this is useful for
loading and returning static pages which do not require context.

"""


setup(
    name='Jinja2Loader',
    version='0.1.0',
    url='http://github.com/schlerp/jinja2loader',
    license='BSD',
    author='schlerp',
    author_email='schlerpderpson@gmail.com',
    description='This module prodives a decorator for using jinja2 templates '
                'with cherry py in an easy way!',
    long_description=__doc__,
    # jinja2loader is egg safe. But we hate eggs, and its a single file...
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    keywords='jinja2 decorator cherrypy',
    py_modules=['jinja2loader'],
    install_requires=['jinja2'],
    include_package_data=True,
)

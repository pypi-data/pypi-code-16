from setuptools import setup, find_packages  # Always prefer setuptools over distutils

long_description = """Create basic MVC skeleton using Web.py microframework
"""

setup(
    name="kuorra",
    version="0.1.3",
    description="Create basic MVC skeleton using Web.py microframework",

    long_description=long_description,
    
    author="Salvador Hernandez Mendoza",
    
    author_email="salvadorhm@gmail.com",
    
    license="GPLv3",
    
    url="https://github.com/salvadorhm/kuorra",
    
    download_url="https://github.com/salvadorhm/kuorra",
    
    classifiers=['Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Intended Audience :: Information Technology',
                'Topic :: Software Development',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Programming Language :: Python :: 2.7'],
    keywords="mvc web.py mysql",
    install_requires=["web.py==0.38", "MySQL-python==1.2.5"],
    zip_safe=False,

    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests", "*tests*"]),
    entry_points={'console_scripts': ['kuorra=kuorra.kuorra:main'],
                },
    package_data={"kuorra": [
            "__init__.py",
            "__main__.py",
            "kuorra.py",
            "mvc/__init__.py",
            "mvc/app.py",
            "mvc/application/__init__.py",
            "mvc/application/controllers/__init__.py",
            "mvc/application/controllers/products/config.py",
            "mvc/application/controllers/products/delete.py",
            "mvc/application/controllers/products/edit.py",
            "mvc/application/controllers/products/index.py",
            "mvc/application/controllers/products/__init__.py",
            "mvc/application/controllers/products/insert.py",
            "mvc/application/controllers/products/view.py",
            "mvc/application/models/config.py",
            "mvc/application/models/__init__.py",
            "mvc/application/models/model_products.py",
            "mvc/application/views/__init__.py",
            "mvc/application/views/products/delete.html",
            "mvc/application/views/products/edit.html",
            "mvc/application/views/products/index.html",
            "mvc/application/views/products/__init__.py",
            "mvc/application/views/products/insert.html",
            "mvc/application/views/products/master.html",
            "mvc/application/views/products/view.html",
            "mvc/data/schema.sql",
            "mvc/static/css/bootstrap.css",
            "mvc/static/css/index.html",
            "mvc/static/files/default.jpg",
            "mvc/static/fonts/glyphicons-halflings-regular.eot",
            "mvc/static/fonts/glyphicons-halflings-regular.svg",
            "mvc/static/fonts/glyphicons-halflings-regular.ttf",
            "mvc/static/fonts/glyphicons-halflings-regular.woff",
            "mvc/static/fonts/glyphicons-halflings-regular.woff2",
            "mvc/static/fonts/index.html",
            "mvc/static/js/bootstrap.js",
            "mvc/static/js/index.html",
            "mvc/static/js/jquery.js"]}
)
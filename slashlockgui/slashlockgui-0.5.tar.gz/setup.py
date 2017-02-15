from setuptools import setup

setup(
    name='slashlockgui',
    version='0.5',
    description='SlashlockGUI - A simple GUI for Slashlock',
    url='https://github.com/wookalar/slashlockgui',
    author='Aaron Hampton',
    author_email='aaron.hampt@gmail.com',
    license='AGPLv3',
    entry_points={'gui_scripts': [
        'slashlockgui = slashlockgui.gui:main',
    ]},
    install_requires=[
        'slashlock>=0.1.5',
        'Cython>=0.24.1',
        'Kivy==1.9.1',
        'Kivy-Garden>=0.1.4',
    ],
    install_package_data=True,
    packages=['slashlockgui'],
    package_data={
        'slashlockgui': ['kvs/*.kv'],
    },
    zip_safe=False,
)

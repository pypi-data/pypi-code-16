from setuptools import setup

setup(
        name='skyCurses',
        version='2.0.8',
        description='Unofficial curses client for the SkyChat',
        url='http://git.beerstorm.info/Beerstorm/SkyCurses',
        author='Beerstorm',
        author_email='beerstorm.emberbeard@gmail.com',
        license='GPLv3',
        packages=['skyCurses'],
        install_requires=[
            'simpleaudio',
            'mplayer.py',
            'pafy',
            'redskyAPI',
            'winCurses>=0.1.5',
            ],
        entry_points = {
            'console_scripts' : [
                'skyCurses = skyCurses.skyCurses:main',
                ],
            },
        package_data = {
            'skyCurses' : [
                'sounds/*.wav',
                'alias.json',
                ],
            },
        zip_safe=False,
        )

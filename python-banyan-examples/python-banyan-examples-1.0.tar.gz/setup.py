from setuptools import setup

setup(
    name='python-banyan-examples',
    version='1.0',
    packages=[
        'python_banyan.examples.clock',
        'python_banyan.examples.digital_toggling',
        'python_banyan.examples.launching',
        'python_banyan.examples.matrix',
        'python_banyan.examples.raspberry_redbot.i2c',
        'python_banyan.examples.raspberry_redbot.i2c.validators',
        'python_banyan.examples.raspberry_redbot.i2c.accelerometers',
        'python_banyan.examples.raspberry_redbot.i2c.a2d',
        'python_banyan.examples.raspberry_redbot.encoders.validators',
        'python_banyan.examples.raspberry_redbot.led',
        'python_banyan.examples.raspberry_redbot.led.validators',
        'python_banyan.examples.raspberry_redbot.buzzer.validators',
        'python_banyan.examples.raspberry_redbot.led.validators',
        'python_banyan.examples.raspberry_redbot.buzzer',
        'python_banyan.examples.raspberry_redbot.buzzer.validators',
        'python_banyan.examples.raspberry_redbot.motors',
        'python_banyan.examples.raspberry_redbot.motors.validators',
        'python_banyan.examples.raspberry_redbot.encoders',
        'python_banyan.examples.raspberry_redbot.switches',
        'python_banyan.examples.raspberry_redbot.gui',
        'python_banyan.examples.raspberry_redbot.i2c.led_matrix',
    ],
    install_requires=[
        'python_banyan',
        'pyzmq',
        'u-msgpack-python',
        'PyMata'
    ],

    package_data={'python_banyan.examples.launching': ['*.txt']},

    entry_points={
        'console_scripts': [
            'clock_gui = python_banyan.examples.clock.clock_gui:clock_gui',
            'tick_counter = python_banyan.examples.clock.tick_counter:tick_counter',
            'tick_generator = python_banyan.examples.clock.tick_generator:tick_generator',
            'binary_clock = python_banyan.examples.clock.binary_clock:binary_clock',

            'rpi_digital_out=python_banyan.examples.digital_toggling.rpi_digital_out:rpi_digital_out',
            'toggler=python_banyan.examples.digital_toggling.toggler:toggler',
            'arduino_digital_out=python_banyan.examples.digital_toggling.arduino_digital_out:arduino_digital_out',

            'lunch_config=python_banyan.examples.launching.lunch_config:lunch_config',

            'i2c_htk1633 = python_banyan.examples.matrix.i2c_htk1633:i2c_htk1633',
            'i2c_pigpio = python_banyan.examples.raspberry_redbot.i2c.i2c_pigpio:i2c_pigpio',

            'buzzer_pigpio = python_banyan.examples.raspberry_redbot.buzzer.buzzer_pigpio:buzzer_pigpio',
            'encoders_pigpio = python_banyan.examples.raspberry_redbot.encoders.encoders_pigpio:encoders_pigpio',
            'i2c_pcf8591 = python_banyan.examples.raspberry_redbot.i2c.a2d.i2c_pcf8591:i2c_pcf8591',
            'i2c_adxl345 = python_banyan.examples.raspberry_redbot.i2c.accelerometers.i2c_adxl345:i2c_adxl345',
            'led = python_banyan.examples.raspberry_redbot.led.led:led',
            'led_pigpio = python_banyan.examples.raspberry_redbot.led.led_pigpio:led_pigpio',
            'motors = python_banyan.examples.raspberry_redbot.motors.motors:motors',
            'motors_pigpio = python_banyan.examples.raspberry_redbot.motors.motors_pigpio:motors_pigpio',
            'switches_gpio = python_banyan.examples.raspberry_redbot.switches.switches_pigpio:switches_pigpio',
            'redbot = python_banyan.examples.raspberry_redbot.gui.redbot_controller:redbot_gui',


        ]
    },
    url='https://github.com/MrYsLab/python_banyan',
    license='GNU General Public License v3 (GPLv3)',
    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    description='A Non-Blocking Event Driven Robotics Framework',
    keywords=['python banyan', 'Raspberry Pi', 'ZeroMQ', 'MessagePack', 'RedBot', ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Education',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Hardware'
    ],
)

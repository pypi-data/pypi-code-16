from setuptools import setup

setup(
    name="SpecClient-for-pyxes",
    version="2017.3.6",
    description="Python package for communicating with spec",
    author="Matias Guijarro, BCU(Bliss), ESRF",
    package_dir={"SpecClient_gevent": "SpecClient"},
    packages=["SpecClient"],
    py_modules=[
        'SpecClient.__init__',
        'SpecClient.saferef',
        'SpecClient.Spec',
        'SpecClient.SpecArray',
        'SpecClient.SpecChannel',
        'SpecClient.SpecClientError',
        'SpecClient.SpecCommand',
        'SpecClient.SpecConnection',
        'SpecClient.SpecConnectionManager',
        'SpecClient.SpecCounter',
        'SpecClient.SpecEventDispatcher',
        'SpecClient.SpecMessage',
        'SpecClient.SpecMotor',
        'SpecClient.SpecReply',
        'SpecClient.SpecScan',
        'SpecClient.SpecServer',
        'SpecClient.SpecVariable',
        'SpecClient.SpecWaitObject',
    ]
)

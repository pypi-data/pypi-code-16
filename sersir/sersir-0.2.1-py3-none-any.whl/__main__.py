"""
This file enables the python interpreter to invoke
our application like this:
    python -m sersir
"""
from sersir.base.settings import conf as config
from sersir.base.runner import Runner

if __name__ == '__main__':
    runner = Runner(config)
    runner.setup()

    runner.run()

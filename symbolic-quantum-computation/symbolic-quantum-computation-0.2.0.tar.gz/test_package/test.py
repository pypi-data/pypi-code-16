import unittest
import src.test_module_a
import src.test_module_a


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='src', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)


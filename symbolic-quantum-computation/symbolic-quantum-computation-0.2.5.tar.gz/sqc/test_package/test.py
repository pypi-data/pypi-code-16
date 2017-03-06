import unittest


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='sqc/tests', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
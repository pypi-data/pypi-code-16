import unittest
import src.test_module_a
import src.test_module_b


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(src.test_module_a)
    suite.addTests(loader.loadTestsFromModule(src.test_module_b))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)


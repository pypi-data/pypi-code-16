import unittest
import sys
import src.test_module_a
import src.test_module_b


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(src.test_module_a)
    suite.addTests(loader.loadTestsFromModule(src.test_module_b))
    suite.addTests(loader.loadTestsFromModule(src.test_module_b.ClassB))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

if __name__ == '__main__':
    main()

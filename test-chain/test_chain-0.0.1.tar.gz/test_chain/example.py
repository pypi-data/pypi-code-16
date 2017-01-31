from test_chain import TestChain


class TestChainExample(TestChain):
    def test_raise_exception(self):
        print("\nTest Raise Message which only happens once")
        raise Exception("Raising Exception")

    def test_pass_test(self, arg=1):
        print ("\nTest Pass Message which only happens once")
        return "Hello World"

    def test_skip_if_sub_test_fails(self):
        """ This should be skipped to show how sub testing failures are skipped """
        print("\nTest Skip Message which only happens once")
        assert self.test_pass_test() == "Hello World" # this will come from cached results
        self.test_raise_exception() # this will throw a UnitTest.SkipException

if __name__ == "__main__":
    import unittest
    print("\n\n\nRunning example of one error, one skipped, and one passed test\n\n\n")
    unittest.main()

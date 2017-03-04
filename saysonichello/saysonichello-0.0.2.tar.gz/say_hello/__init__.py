import hello
import sys


def main():
    """
    Entry point for the application script
    Call your main application code here
    """
    if len(sys.argv) > 1:
        args = sys.argv[1]
        hello.hello(args)

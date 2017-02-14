import sys
import test
from src import foo


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Do something here
    for flag in args:
        if flag == '-t':
            test.run_tests()
        else:
            foo.bar()
            print('Nothing to do!')

if __name__ == '__main__':
    main()

import sys
from src import foo
import test


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Do something here
    for flag in args:
        if flag == '-t':
            test.run_tests()
            pass
        else:
            foo.bar()
            print('Nothing to do!')

if __name__ == '__main__':
    main()

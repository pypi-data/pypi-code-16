import sys
# import test.test
from src import bar


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Do something here
    for flag in args:
        if flag == '-t':
            # test.test.run_tests()
            pass
        else:
            bar()
            print('Nothing to do!')

if __name__ == '__main__':
    main()

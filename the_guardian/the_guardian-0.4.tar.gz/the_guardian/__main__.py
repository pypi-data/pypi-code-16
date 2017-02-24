import scheduler
import sys


def main(args=None):
    """The main routine."""
    
    if len(sys.argv) < 2:
        scheduler.guardian()
    else:
        scheduler.guardian(sys.argv[1])

if __name__ == "__main__":
    main()
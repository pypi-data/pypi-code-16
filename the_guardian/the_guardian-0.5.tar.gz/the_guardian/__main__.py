import scheduler
import sys


def main(args=None):
    """The main routine."""
    
    if len(sys.argv) < 3:
        scheduler.guardian()
    else:
        scheduler.guardian(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
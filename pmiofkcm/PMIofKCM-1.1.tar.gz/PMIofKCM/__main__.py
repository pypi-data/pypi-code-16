import sys
from PMIofKCM import PMI

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1]

    p = PMI(args)
    p.build()
    print(p.get("臺灣", 10))

if __name__ == "__main__":
    main()
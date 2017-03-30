import sys
from .envr import Envr


def main():
    e = Envr(None, stream=sys.stdin)
    sys.stdout.write(e.env(strict=True))


if __name__ == "__main__":
    main()

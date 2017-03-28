import sys
from main import main
from SilentException import SilentException

try:
    main(sys.argv[1:])
except SilentException:
    pass


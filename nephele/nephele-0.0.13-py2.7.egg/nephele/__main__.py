from main import main
import sys

try:
    main(sys.argv[1:])
except SilentException:
    pass


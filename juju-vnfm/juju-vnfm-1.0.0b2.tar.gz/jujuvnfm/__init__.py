import sys

if sys.version_info[0] < 2:
    raise Exception("At least Python 2.7.12 is required")
elif sys.version_info[0] == 2:
    if sys.version_info[1] < 7:
        raise Exception("At least Python 2.7.12 is required")
    elif sys.version_info[1] == 7 and sys.version_info[2] < 12:
        raise Exception("At least Python 2.7.12 is required")

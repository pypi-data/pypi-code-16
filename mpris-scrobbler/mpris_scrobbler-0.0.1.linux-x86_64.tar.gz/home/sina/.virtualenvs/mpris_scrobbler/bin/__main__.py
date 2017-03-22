#!/home/sina/.virtualenvs/mpris_scrobbler/bin/python
import mpris_scrobbler
from sys import exit

if __name__ == "__main__":
    try:
        mpris_scrobbler.run()
    except KeyboardInterrupt:
        exit("\n")

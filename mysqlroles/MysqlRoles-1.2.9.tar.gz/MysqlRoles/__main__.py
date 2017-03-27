from MysqlRoles import Run
import sys

if __name__ == "__main__":
    r = Run()
    helpstr = \
    """Expected Command Line Usage of MysqlRoles:
    init (address/name for central server)
        creates empty tables
    seed (address/name for central server)
        seeds with test info
    update (address/name for central server) (address/name for host)
        updates the host as requested."""
    if len(sys.argv)<2:
        print(helpstr)
    else:
        s = r.parse(sys.argv[1:])

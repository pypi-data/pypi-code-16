from MysqlRoles import RoleManage
from MysqlRoles import RoleServ
import pymysql
import os

class Run(object):

    @staticmethod
    def parse(args):
        """
        Parse arguments given to CLI into commands to run.
        """
        # -- Desired Commands
        # init (address/name for central server) -- creates empty tables
        # seed (address/name for central server) -- seeds with test info
        # update (address/name for central server) (address/name for host)
        # -- updates the host as requested
        helpstr = \
        """Expected Command Line Usage of MysqlRoles:
        init (address/name for central server)
            creates empty tables
        seed (address/name for central server)
            seeds with test info
        update (address/name for central server) (address/name for host)
            updates the host as requested."""
        if len(args) < 1:
            print(helpstr)
            return 1
        elif args[0].lower() == "init":
            if len(args) not in (1,2):
                print("init expects 0 or 1 additional arguments, try running help")
                return 1
            else:
                if len(args)==1:
                    cent = Run.net_test("localhost")
                else:
                    cent = Run.net_test(args[1])
                rs = RoleServ(cent)
                rs.create_tables()
                print("created tables on {}".format(cent))
                return 0
        elif args[0].lower() == "seed":
            if len(args) not in (1,2):
                print("seed expects 0 or 1 additional arguments, try running help")
                return 1
            else:
                if len(args)==1:
                    cent = Run.net_test("localhost")
                else:
                    cent = Run.net_test(args[1])
                rs = RoleServ(cent)
                rs.test_seed_tables()
                print("test seeded on {}".format(cent))
                return 0
        elif args[0].lower() == "update":
            if len(args) not in (2,3):
                print("update expects 1 or 2 additional arguments, try running help")
                return 1
            else:
                cent = Run.net_test(args[1])
                if len(args)==2:
                    client = Run.net_test("localhost")
                else:
                    client = Run.net_test(args[2])
                rm = RoleManage(cent, client)
                rm.update_users()
                print("updated users on {} from {}".format(client, cent))
                return 0
        else:
            print(helpstr)
            return 1

    @staticmethod
    def net_test(host):
        """
        Determine if a host is accessible before doing anything.

        Returns the host name back if the host is up and is able to connect with mysql.
        To fix this issue, try:
        - Update your my.cnf with credentials
        - Start a mysql instance on the host
        """
        cnf_file = os.path.expanduser('~/.my.cnf')
        try:
            pymysql.connect(host=host, db='mysql', read_default_file=cnf_file)
            return host
        except pymysql.err.OperationalError:
            return False
        pass

__author__ = 'rajatv'
from migrations import Migrations


class QdsApp(object):
    @classmethod
    def setup_parsers(cls, sub_parser):
        cls.generate_parser = sub_parser.add_parser("generate",
                                                    help="Generate a new migration")
        cls.generate_parser.add_argument("-m", "--message", required=True,
                                         help="Provide a message describing the migration")
        cls.generate_parser.set_defaults(func=cls.generate_cmd)

        cls.upgrade_parser = sub_parser.add_parser("upgrade",
                                                   help="Run pending migrations")

        cls.upgrade_parser.add_argument("-current", "--current", help="Provide the current version")
        cls.upgrade_parser.add_argument("-id", "--id", help="Provide version of the migration to run")
        cls.upgrade_parser.add_argument("-defloc", "--default_location", required=False,
                                        help="Provide the default location of the Qubole account. ")
        cls.upgrade_parser.set_defaults(func=cls.upgrade_cmd)

        cls.downgrade_parser = sub_parser.add_parser("downgrade", help="downgrade to a migration")
        cls.downgrade_parser.add_argument("-rev", "--revision", help="Provide revision id to downgrade to")
        cls.downgrade_parser.add_argument("-id", "--id", help="Provide version of the migration to revert")

        cls.downgrade_parser.set_defaults(func=cls.downgrade_cmd)

        cls.list_parser = sub_parser.add_parser("list",
                                                help="List all migrations")
        cls.list_parser.set_defaults(func=cls.list_cmd)

        cls.dag_parser = sub_parser.add_parser("dag", help="Create Airflow Script")
        cls.dag_parser.add_argument("-d", "--date", default="2016-02-01 02:00", help="Start date of airflow script")
        cls.dag_parser.add_argument("-f", "--file", help="File Path to store the airflow script", default="dag.py")
        cls.dag_parser.set_defaults(func=cls.dag_cmd)

        cls.deploy_parser = sub_parser.add_parser("deploy", help="Deploy a version of Mojave")
        cls.deploy_parser.add_argument("-l", "--label", help="Cluster Label of Airflow Cluster", default="airflow")
        cls.deploy_parser.add_argument("-r", "--revision", help="Version of Mojave", default="HEAD")
        cls.deploy_parser.add_argument("-d", "--date", default="2016-02-01 02:00", help="Start date of airflow script")
        cls.deploy_parser.set_defaults(func=cls.deploy_cmd)

    @classmethod
    def generate_cmd(cls, args):
        obj = cls(args)
        obj.migrations.generate(obj.args.message)

    @classmethod
    def list_cmd(cls, args):
        obj = cls(args)
        revs = obj.migrations.list()
        for r in revs:
            print str(r)

    @classmethod
    def upgrade_cmd(cls, args):
        obj = cls(args)
        obj.migrations.upgrade(version=obj.args.id)

    @classmethod
    def downgrade_cmd(cls, args):
        obj = cls(args)
        if obj.args.revision is None:
            obj.migrations.downgrade(version=obj.args.id)
        else:
            obj.migrations.downgrade(revision=int(obj.args.revision), version=obj.args.id)

    @classmethod
    def dag_cmd(cls, args):
        obj = cls(args)
        obj.dag()

    @classmethod
    def deploy_cmd(cls, args):
        obj = cls(args)
        obj.deploy()

    def __init__(self, args, base_path, current):
        self.args = args
        self.base_path = base_path
        self.migrations = Migrations("%s/migrations" % base_path, current=current)

    def dag(self):
        raise NotImplementedError

    def deploy(self):
        raise NotImplementedError

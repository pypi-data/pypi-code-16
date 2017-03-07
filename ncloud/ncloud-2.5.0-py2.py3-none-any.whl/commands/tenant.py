# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for adding/deleting/modifying and listing tenants - admin
privileges required.
"""
from functools import partial

from ncloud.commands.command import Command, NoRespCommand, build_subparser
from ncloud.commands.command import ADD, MODIFY, LS, RM, SHOW
from ncloud.formatting.output import print_table
from ncloud.util.api_call import api_call_json
from ncloud.config import TENANTS


class Add(NoRespCommand):
    """
    Add a new tenant to the cloud.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(ADD.name, aliases=ADD.aliases,
                                      help=Add.__doc__,
                                      description=Add.__doc__)
        parser.add_argument("name",
                            type=str,
                            help="new tenant's name")
        parser.add_argument("-t", "--tflops",
                            type=int,
                            help="tflop limit")
        parser.add_argument("-n", "--numhosts",
                            type=int,
                            help="allowed host count")
        parser.add_argument("-r", "--ram",
                            type=int,
                            help="RAM limit in GB")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, name, tflops=None, numhosts=None, ram=None):
        data = {}
        data["name"] = name
        endpoint = TENANTS
        method = "POST"
        return api_call_json(config, endpoint=endpoint,
                             method=method, data=data)


class Modify(NoRespCommand):
    """
    Update the attributes of an individual tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(MODIFY.name, aliases=MODIFY.aliases,
                                      help=Modify.__doc__,
                                      description=Modify.__doc__)
        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to be modified")
        parser.add_argument("name",
                            type=str,
                            help="tenant's new name")
        parser.add_argument("-t", "--tflops",
                            type=int,
                            help="new tflop limit")
        parser.add_argument("-n", "--numhosts",
                            type=int,
                            help="new allowed host count")
        parser.add_argument("-r", "--ram",
                            type=int,
                            help="new RAM limit in GB")
        parser.add_argument("-e", "--enabled",
                            type=int,
                            help="0 = disabled, 1 = enabled")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id, name=None, tflops=None, numhosts=None,
             ram=None, enabled=None):
        data = {}
        data["operation"] = "replace"
        if name is not None:
            data["name"] = name
        if tflops is not None:
            data["tflops"] = tflops
        if numhosts is not None:
            data["numhosts"] = numhosts
        if ram is not None:
            data["ram"] = ram
        if enabled is not None:
            data["enabled"] = enabled

        endpoint = TENANTS + str(tenant_id)
        method = "PATCH"
        return api_call_json(config, endpoint=endpoint,
                             method=method, data=data)


class Remove(NoRespCommand):
    """
    Delete a tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(RM.name, aliases=RM.aliases,
                                      help=Remove.__doc__,
                                      description=Remove.__doc__)

        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to be deleted")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id):
        endpoint = TENANTS + str(tenant_id)
        method = "DELETE"
        return api_call_json(config, endpoint=endpoint, method=method)


class List(Command):
    """
    List tenants.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(LS.name, aliases=LS.aliases,
                                      help=List.__doc__,
                                      description=List.__doc__)
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        endpoint = TENANTS
        method = "GET"
        return api_call_json(config, endpoint=endpoint, method=method)

    @staticmethod
    def display_after(config, args, res):
        if not res:
            print_table({"error": "Error: no response from Helium"})
        else:
            print_table(res['tenants'])


class Show(Command):
    """
    Display details of an individual tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                      help=Show.__doc__,
                                      description=Show.__doc__)

        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to show details of.")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id):
        endpoint = TENANTS + str(tenant_id)
        method = "GET"
        return api_call_json(config, endpoint=endpoint, method=method)

    @staticmethod
    def display_after(config, args, res):
        if not res:
            print_table({"error": "Error: no response from Helium"})
        else:
            print_table(res['tenant'])


parser = partial(
    build_subparser, 'tenant', ['t'], __doc__,
    (Add, Modify, Remove, List, Show)
)

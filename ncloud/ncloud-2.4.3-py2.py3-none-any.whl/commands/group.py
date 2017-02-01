# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for adding/deleting/modifying and listing user membership
collections - admin privileges required.
"""
from functools import partial

from ncloud.commands.command import Command, NoRespCommand, build_subparser
from ncloud.commands.command import LS, ADD, SHOW, RM, MODIFY
from ncloud.formatting.output import print_table
from ncloud.util.api_call import api_call_json
from ncloud.config import USERS, TENANTS


class Add(NoRespCommand):
    """
    Add a new user grouping to a tenant.
    """

    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(ADD.name, aliases=ADD.aliases,
                                      help=Add.__doc__,
                                      description=Add.__doc__)
        parser.add_argument("name",
                            type=str,
                            help="new groups's name")
        parser.add_argument("tenant_id",
                            type=int,
                            help="tenant to which this group belongs")
        parser.add_argument("capability",
                            type=int,
                            help="privilege level")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, name, tenant_id, capability):
        data = {}
        endpoint = TENANTS + str(tenant_id)
        method = "PATCH"
        data["operation"] = "add"
        data["groups"] = [name]
        data["capabilities"] = capability
        return api_call_json(config,
                             endpoint=endpoint,
                             method=method,
                             data=data)


class Modify(NoRespCommand):
    """
    Update the attributes of an individual group.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(MODIFY.name, aliases=MODIFY.aliases,
                                      help=Modify.__doc__,
                                      description=Modify.__doc__)
        parser.add_argument("group_id",
                            type=int,
                            help="ID of group to update")
        parser.add_argument("-n", "--name",
                            type=str,
                            help="new name")
        parser.add_argument("-c", "--capabilities",
                            type=int,
                            help="new capabilities")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, group_id, name=None, capabilities=None):
        data = {}
        data["operation"] = "replace"
        if name is not None:
            data["name"] = name
        if capabilities is not None:
            data["capabilities"] = capabilities

        endpoint = TENANTS + "groups/" + str(group_id)
        method = "PATCH"
        return api_call_json(config, endpoint=endpoint,
                             method=method, data=data)


class Remove(NoRespCommand):
    """
    Delete a user grouping.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(RM.name, aliases=RM.aliases,
                                      help=Remove.__doc__,
                                      description=Remove.__doc__)

        parser.add_argument("tenant_id",
                            type=int,
                            help="tenant_id to which this group belongs")
        parser.add_argument("group_id",
                            type=int,
                            help="id of group to be deleted")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id, group_id):
        data = {}
        endpoint = TENANTS + str(tenant_id)
        method = "PATCH"
        data["operation"] = "remove"
        data["groups"] = [group_id]
        return api_call_json(config,
                             data=data,
                             endpoint=endpoint,
                             method=method)


class List(Command):
    """
    Display list of groups for a tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(LS.name, aliases=LS.aliases,
                                      help=List.__doc__,
                                      description=List.__doc__)

        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to show groups for.")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id):
        endpoint = TENANTS + "groups/" + str(tenant_id)
        method = "GET"
        return api_call_json(config, endpoint=endpoint, method=method)

    @staticmethod
    def display_after(config, args, res):
        if not res:
            print_table({"error": "Error: no response from Helium"})
        else:
            print_table(res['tenant'])


class Show(Command):
    """
    Show members of a particular group.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                      help=Show.__doc__,
                                      description=Show.__doc__)
        parser.set_defaults(func=cls.arg_call)

        parser.add_argument("group_id",
                            type=int,
                            help="group_id for which to list members for")

    @staticmethod
    def call(config, group_id):
        endpoint = USERS + "groups/" + str(group_id)
        method = "GET"
        return api_call_json(config,
                             endpoint=endpoint,
                             method=method)

    @staticmethod
    def display_after(config, args, res):
        if not res:
            print_table({"error": "Error: no response from Helium"})
        else:
            print_table(res['users'])


parser = partial(
    build_subparser, 'group', ['g'], __doc__,
    (List, Add, Remove, Show, Modify)
)

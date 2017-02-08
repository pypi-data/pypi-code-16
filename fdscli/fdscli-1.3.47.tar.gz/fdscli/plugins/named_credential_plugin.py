# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import json
import time
from fdscli.services import response_writer
from fdscli.services.subscription.named_credential_client import NamedCredentialClient
from fdscli.utils.converters.common.named_credential_converter import NamedCredentialConverter
from .abstract_plugin import AbstractPlugin
from fdscli.model.common.size import Size
from fdscli.model.fds_error import FdsError
from fdscli.services.fds_auth import FdsAuth
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.common.repository import Repository
from collections import OrderedDict

class NamedCredentialPlugin(AbstractPlugin):
    '''Provides named credential management.

    Creates command line parsers and uses Formation Named Credential service client to
    dispatch requests.

    Attributes
    ----------
    :type _NamedCredentialPlugin__credential_client: ``services.subscription.NamedCredentialClient``
    :attr _NamedCredentialPlugin__credential_client: Low-level API for HTTP named credential API

    :type _NamedCredentialPlugin__parser: ``argparse.ArgumentParser``
    :type _NamedCredentialPlugin__subparser: ``argparse._SubParsersAction``
    '''

    def __init__(self):
        AbstractPlugin.__init__(self)

    def build_parser(self, parentParser, session):
        '''
        @see: AbstractPlugin

        Parameters
        ----------
        parentParser (argparse.Action)
        session (services.FdsAuth)
        '''
        
        self.session = session
        
        self.__credential_client = NamedCredentialClient( self.session )

        msg = ("Named credential management. Stores credentials securely for use by SafeGuard "
            "recurring data migration tasks. A named credential specifies the URL of a data "
            "storage endpoint and the authentication arguments required to access the data.")
        self.__parser = parentParser.add_parser("credential", description=msg, help=msg)
        self.__subparser = self.__parser.add_subparsers(title="subcommands",
            description="credential subcommands",
            help="description:")

        # Add parsers for sub-commands
        self.add_command_delete(self.__subparser)
        self.add_command_list(self.__subparser)
        self.add_command_save(self.__subparser)

    def detect_shortcut(self, args):

        return None

    def add_command_delete(self, subparser):
        '''
        Creates the parser for the ``credential delete`` sub-command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        __parserForDelete = subparser.add_parser("delete", help=("Delete a named credential "
            "for the current user. Does not deactivate the authentication arguments for the "
            "storage endpoint indicated by the named credential."))

        # Optional args
        __parserForDelete.add_argument(self.arg_str + AbstractPlugin.name_str, help=("The user "
            "defined credential name."), required=False)
        __parserForDelete.add_argument(self.arg_str + AbstractPlugin.id_str, help=("The unique "
            "identifier for the named credential."), required=False)

        __parserForDelete.set_defaults(func=self.delete_named_credential, format="tabular")

    def add_command_list(self, subparser ):
        '''
        Creates the parser for the ``credential list`` sub-command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        __parserForList = subparser.add_parser( "list", help="List named credentials for the current user.")

        # Optional args
        self.add_format_arg(__parserForList)
        __parserForList.add_argument(self.arg_str + AbstractPlugin.name_str, help=("The user "
            "defined credential name."), required=False)
        __parserForList.add_argument(self.arg_str + AbstractPlugin.id_str, help=("The unique "
            "identifier for the named credential."), required=False)
        
        __parserForList.set_defaults(func=self.list_named_credentials, format="tabular")

    def add_command_save(self, subparser):
        '''
        Creates the parser for the ``credential save`` sub-command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        help_save = ("Save a named credential for the current user. This command saves user "
            "supplied authentication arguments, along with a URL, and associates them with "
            "a user supplied name. This command can not be used to create new authentication "
            "arguments for an endpoint. For example, remote OM credentials can be saved on the "
            "local domain, but those credentials are owned by and managed on the remote OM.")
        __parserForSave = subparser.add_parser("save", description=help_save, help=help_save)

        parserForSaveSubParser = __parserForSave.add_subparsers(help="Available sub-commands.")

        # 'credential save s3' sub-command
        msg_save_s3 = ("Save S3 named credential. Used for data migration to an existing S3 bucket.")
        __parserForSaveS3 = parserForSaveSubParser.add_parser("s3", description=msg_save_s3, help=msg_save_s3)

        __parserForSaveS3.add_argument("CREDENTIAL_NAME", help=("The credential "
            "name. Must be unique for the user. Spaces are invalid in the name."),
            default=None)
        __parserForSaveS3.add_argument("URL", help=("S3 endpoint "
            "like 'https://s3-us-west2.amazonaws.com'."))
        __parserForSaveS3.add_argument("BUCKET_NAME",
            help=("For a S3 endpoint, specifies the bucket name. The bucket must exist prior to "
            "data access."))
        __parserForSaveS3.add_argument("ACCESS_KEY",
            help=("For a S3 endpoint, specifies the AWS Credentials access key."))
        __parserForSaveS3.add_argument("SECRET_KEY",
            help=("For a S3 endpoint, specifies the AWS Credentials secret key."))

        __parserForSaveS3.set_defaults(func=self.save_named_credential_s3, format="json")

        # 'credential save f1' sub-command
        msg_save_f1 = ("Save FormationOne named credential. Used for data migration to a remote OM node.")
        __parserForSaveF1 = parserForSaveSubParser.add_parser("f1", description=msg_save_f1, help=msg_save_f1)

        __parserForSaveF1.add_argument("CREDENTIAL_NAME", help=("The credential "
            "name. Must be unique for the user. Spaces are invalid in the name."), default=None)
        __parserForSaveF1.add_argument("PROTOCOL", type=str, choices=['http','https'],
            help=("For a FormationOne endpoint, the protocol. Recommended value is 'https'."))
        __parserForSaveF1.add_argument("REMOTE_USERNAME",
            help=("Name of a FormationOne user for the remote OM."), default=None)
        __parserForSaveF1.add_argument("REMOTE_PASSWORD",
            help=("Password for the FormationOne user on the remote OM."), default=None)
        __parserForSaveF1.add_argument("REMOTE_HOSTNAME",
            help=("Hostname for the remote OM."), default=None)
        __parserForSaveF1.add_argument("PORT", nargs='?', help=("Port number for the remote OM."), type=int, default=0)

        __parserForSaveF1.set_defaults(func=self.save_named_credential_f1, format="json")

    def get_named_credential_client(self):
        return self.__credential_client

    def delete_named_credential(self, args):
        '''
        Parameters
        ----------
        :type args: dict
        '''
        digest = None
        name = None
        if AbstractPlugin.id_str in args and args[AbstractPlugin.id_str] is not None:
            digest = args[AbstractPlugin.id_str]
        elif AbstractPlugin.name_str in args and args[AbstractPlugin.name_str] is not None:
            name = args[AbstractPlugin.name_str]

        if digest is None and name is None:
            print("Missing identifier or name.\n")
            return

        response = None
        key = None
        if digest is not None:
            key = digest
            response = self.get_named_credential_client().delete_named_credential(digest)
        elif name is not None:
            key = name
            named_credential = self.get_named_credential_client().get_named_credential_by_key(name)
            if not isinstance(named_credential, NamedCredential):
                print("Named credential '{}' not found.\n".format(name))
                return
            response = self.get_named_credential_client().delete_named_credential(named_credential.digest)

        if isinstance(response, FdsError):
            return

        print("Named credential '{}' deleted.\n".format(key))
        return

    def print_list_result(self, named_credentials, print_json):
        '''
        Parameters
        ----------
        :type named_credentials: list(``model.common.NamedCredential``)
        :type print_json: bool
        '''
        if print_json is True:

            j_named_credentials = []

            for named_credential in named_credentials:
                j_named_cred = NamedCredentialConverter.to_json(named_credential)
                j_named_cred = json.loads(j_named_cred)
                j_named_credentials.append(j_named_cred)

            response_writer.ResponseWriter.writeJson(j_named_credentials)
        else:
            # Sort into two piles
            s3credentials = []
            f1credentials = []
            for named_credential in named_credentials:
                # An S3 credential is supposed to have a bucketname. An F1 credential should not.
                # If there is an S3 bucketname string, and it is not empty string, put it into
                # the S3 credentials list.
                if named_credential.bucketname is not None and len(str(named_credential.bucketname)) > 0:
                    s3credentials.append(named_credential)
                else:
                    f1credentials.append(named_credential)
            if (len(s3credentials) > 0):
                resultList = response_writer.ResponseWriter.prep_s3credentials_for_table(self.session, s3credentials)
                response_writer.ResponseWriter.writeTabularData(resultList)
            if (len(f1credentials) > 0):
                resultList = response_writer.ResponseWriter.prep_f1credentials_for_table(self.session, f1credentials)
                response_writer.ResponseWriter.writeTabularData(resultList)

    def get_named_credential_by_digest(self, digest):
        '''
        Parameters
        ----------
        :type name: string
        :param digest: The unique id (digest) of the named credential

        Returns
        -------
        :type ``model.common.NamedCredential``
        '''
        if digest is None:
            return
        if len(digest) == 0:
            return

        response = self.get_named_credential_client().get_named_credential(digest)
        return response

    def get_named_credential_by_name(self, name):
        '''
        Parameters
        ----------
        :type name: string
        :param name: The name of the named credential, which is unique per user

        Returns
        -------
        :type ``model.common.NamedCredential``
        '''
        if name is None:
            return
        if len(name) == 0:
            return

        response = self.get_named_credential_client().get_named_credentials()

        if isinstance(response, FdsError):
            return response

        if isinstance(response, collections.Iterable):
            for named_credential in response:
                if named_credential.name == name:
                    return named_credential

        return

    def list_named_credentials(self, args):
        '''
        Parameters
        ----------
        :type args: dict
        '''
        print_json = False
        if "format" in args and args[AbstractPlugin.format_str] == "json":
            print_json = True

        if AbstractPlugin.id_str in args and args[AbstractPlugin.id_str] is not None:
            # Get by digest
            digest = args[AbstractPlugin.id_str]
            named_credential = self.get_named_credential_by_digest(digest)
            if named_credential is None:
                print("Not Found: Named credential with Id '{}'.\n".format(digest))
                return
            if isinstance(named_credential, FdsError):
                return

            # Render
            named_credentials = [named_credential]
            self.print_list_result(named_credentials, print_json)
            return

        if AbstractPlugin.name_str in args and args[AbstractPlugin.name_str] is not None:
            # Get by name
            name = args[AbstractPlugin.name_str]
            named_credential = self.get_named_credential_by_name(name)
            if named_credential is None:
                print("Not Found: Named credential with name '{}'.\n".format(name))
                return
            if isinstance(named_credential, FdsError):
                return

            # Render
            named_credentials = [named_credential]
            self.print_list_result(named_credentials, print_json)
            return

        # Get all
        response = self.get_named_credential_client().get_named_credentials()

        if isinstance(response, FdsError):
            return

        if (len(response) == 0):
            print("No named credentials for this user.")
            return

        self.print_list_result(response, print_json)

    def save_named_credential_f1(self, args):
        '''
        Parameters
        ----------
        :type args: dict
        '''
        credential = NamedCredential()

        # Required positional args
        credential.protocol = args["PROTOCOL"]
        credential.username = args["REMOTE_USERNAME"]
        credential.password = args["REMOTE_PASSWORD"]
        credential.hostname = args["REMOTE_HOSTNAME"]
        credential.port = int(args["PORT"])

        if (credential.port == 0):
            if (credential.protocol == 'http'):
                credential.port = int(7777)
            else:
                credential.port = int(7443)

        credential.name = args["CREDENTIAL_NAME"]
        credential.user_id = self.session.get_user_id()

        credential.url = credential.protocol;
        if credential.url.find("://") == -1:
            if credential.url.find(":/") == -1:
                credential.url += "://"
            else:
                credential.url += "/"

        credential.url += credential.username
        credential.url += ":"
        credential.url += credential.password
        credential.url += "@"
        credential.url += credential.hostname
        credential.url += ":"
        credential.url += str(credential.port)

        # Check for existence
        existing = self.get_named_credential_by_name(credential.name)
        if (isinstance(existing, NamedCredential)):
            credential.digest = existing.digest
            response = self.get_named_credential_client().update_named_credential(credential)
        else:
            response = self.get_named_credential_client().create_named_credential(credential)

        if isinstance(response, FdsError):
            return

        use_json = False
        if args["format"] is not None and args["format"] == "json":
            use_json = True

        if (isinstance(response, NamedCredential)):
            credentials = []
            credentials.append(response)
            self.print_list_result(credentials, use_json)

        return

    def save_named_credential_s3(self, args):
        '''
        Parameters
        ----------
        :type args: dict
        '''
        credential = NamedCredential()

        # Required positional args
        credential.url = args["URL"]
        credential.name = args["CREDENTIAL_NAME"]
        credential.user_id = self.session.get_user_id()
        credential.bucketname = args["BUCKET_NAME"]
        s3credentials = S3Credentials()
        s3credentials.access_key_id = args["ACCESS_KEY"]
        s3credentials.secret_key = args["SECRET_KEY"]
        credential.s3credentials = s3credentials
        # Check for existence
        existing = self.get_named_credential_by_name(credential.name)
        if (isinstance(existing, NamedCredential)):
            credential.digest = existing.digest
            response = self.get_named_credential_client().update_named_credential(credential)
        else:
            response = self.get_named_credential_client().create_named_credential(credential)

        if isinstance(response, FdsError):
            return

        use_json = False
        if args["format"] is not None and args["format"] == "json":
            use_json = True

        if (isinstance(response, NamedCredential)):
            credentials = []
            credentials.append(response)
            self.print_list_result(credentials, use_json)

        return

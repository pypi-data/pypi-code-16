# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import json
from fdscli.services.abstract_service import AbstractService
from fdscli.model.fds_error import FdsError
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.repository import Repository
from fdscli.utils.converters.common.named_credential_converter import NamedCredentialConverter

class NamedCredentialClient(AbstractService):
    '''
    Formation Named Credential
    Formation Named Credential is a web service that enables a user to manage named credentials.
    A named credential encapsulates the endpoint for a SafeGuard data migration task along with
    the authentication parameters required to access the endpoint.

    Client
    This low-level API provides one-to-one mappings to the underlying HTTP API operations.
    '''

    def __init__(self, session):
        '''
        :type session: ``services.FdsAuth``
        :param session: Data about the active session
        '''
        AbstractService.__init__(self, session)

    def create_named_credential(self, named_credential):
        '''
        Adds a persistent named credential for the current user.

        Parameters
        ----------
        :type named_credential: ``model.common.NamedCredential`` object

        Returns
        -------
        :type ``model.FdsError`` or ``model.common.NamedCredential``
        '''
        url = "{}{}".format(self.get_url_preamble(), "/named_credentials")
        data = NamedCredentialConverter.to_json(named_credential)
        response = self.rest_helper.post(self.session, url, data)

        if isinstance(response, FdsError):
            return response

        deserialized = NamedCredentialConverter.build_from_json(response)
        return deserialized        

    def get_f1_repository(self, credential_key):
        '''
        Gets a named credential and converts it to a Repository object.
        A F1 differentiated ``model.commmon.Repository`` is required in the body for HTTP
        POST 'volumes/#/exports'.

        Parameters
        ----------
        :type credential_key: string

        Returns
        -------
        :type ``model.FdsError`` or ``model.common.Repository`` or None
        '''
        if credential_key is None:
            return
        if len(credential_key) == 0:
            return

        repository = Repository()
        named_credential = self.get_named_credential_by_key(credential_key)
        if isinstance(named_credential, FdsError):
            return named_credential

        if isinstance(named_credential, NamedCredential):
            if named_credential.isF1Credential() == False:
                print("Not a F1 named credential: '{}'.\n".format(credential_key))
                return
            repository.url = named_credential.url
        else:
            print("No named credential found for '{}'.\n".format(credential_key))
            return
        return repository

    def get_s3_repository(self, credential_key):
        '''
        Gets a named credential and converts it to a Repository object.
        A S3 differentiated ``model.commmon.Repository`` is required in the body for HTTP
        POST 'volumes/#/exports/s3' and POST 'volumes/import/s3'.

        Parameters
        ----------
        :type credential_key: string

        Returns
        -------
        :type ``model.FdsError`` or ``model.common.Repository`` or None
        '''
        if credential_key is None:
            return
        if len(credential_key) == 0:
            return

        repository = Repository()
        named_credential = self.get_named_credential_by_key(credential_key)
        if isinstance(named_credential, FdsError):
            return named_credential

        if isinstance(named_credential, NamedCredential):
            if named_credential.isS3Credential() == False:
                print("Not a S3 named credential: '{}'.\n".format(credential_key))
                return

            repository.credentials.access_key_id = named_credential.s3credentials.access_key_id
            repository.credentials.secret_key = named_credential.s3credentials.secret_key
            repository.bucket_name = named_credential.bucketname
            repository.url = named_credential.url
        else:
            print("No named credential found for '{}'.\n".format(credential_key))
            return
        return repository

    def get_named_credential(self, digest):
        '''
        Parameters
        ----------
        :type digest: string
        :param digest: Unique identifier for a named credential

        Returns
        -------
        :type ``model.FdsError`` or ``model.common.NamedCredential``
        '''
        if digest is None:
            return
        if len(digest) == 0:
            return

        # TODO: Add GET for /named_credentials/:digest
        response = self.get_named_credentials()

        if isinstance(response, FdsError):
            return response

        for named_credential in response:
            if (named_credential.digest == digest):
                return named_credential

        return

    def get_named_credential_by_key(self, key):

        if key is None:
            return None
        if len(key) == 0:
            return None

        response = self.get_named_credentials()

        if isinstance(response, FdsError):
            return response

        # Valid keys are digest or name
        if isinstance(response, collections.Iterable):
            for named_credential in response:
                if named_credential.name == key or named_credential.digest == key:
                    return named_credential

        return

    def get_named_credentials(self):
        '''
        Returns
        -------
        :type ``model.FdsError`` or list(``model.common.NamedCredential``)
        '''
        url = "{}{}".format(self.get_url_preamble(), "/named_credentials")
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        named_credentials = []

        for j_str in response:
            named_credential = NamedCredentialConverter.build_from_json(j_str)
            named_credentials.append(named_credential)

        return named_credentials

    def delete_named_credential(self, digest):
        '''
        Deletes existing persistent named credential for the current user.

        Parameters
        ----------
        :type digest: string

        Returns
        -------
        :type ``model.FdsError`` or bool
        '''
        if digest is None:
            return False
        url = "{}{}{}".format(self.get_url_preamble(), "/named_credentials/", digest)
        response = self.rest_helper.delete(self.session, url)

        if isinstance(response, FdsError):
            return response

        # TODO: What if not found or other failure to delete?
        return True

    def update_named_credential(self, named_credential):
        '''
        Updates existing persistent named credential for the current user.

        Parameters
        ----------
        :type named_credential: ``model.common.NamedCredential`` object

        Returns
        -------
        :type ``model.FdsError`` or ``model.common.NamedCredential``
        '''
        url = "{}{}{}".format(self.get_url_preamble(), "/named_credentials/",
            named_credential.digest)
        data = NamedCredentialConverter.to_json(named_credential)
        response = self.rest_helper.put(self.session, url, data)

        if isinstance(response, FdsError):
            return response

        # No error response, so fetch the credential for display
        return self.get_named_credential(named_credential.digest)


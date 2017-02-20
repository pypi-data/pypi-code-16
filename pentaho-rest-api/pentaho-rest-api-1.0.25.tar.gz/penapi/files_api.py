import logging
import xmltodict
import json

from constants import (
    PENTAHO_FILES_ENDPOINT_API,
    CREATE_DIRECTORY,
    LIST_DIRECTORY,
    GET_ACL,
    SET_ACL
)

from penapi.base_api import PentahoBaseAPI

logger = logging.getLogger(__name__)


class PentahoFilesAPI(PentahoBaseAPI):

    def directory_to_url_path(self, directory):
        return directory.replace('/', ':').replace('\\', ':')

    def create_directory(self, path):
        """
        Create a directory
        :param path: full directory's path
        :return: success/failure
        :rtype: bool
        """
        response = self._pentaho.make_call(
            PENTAHO_FILES_ENDPOINT_API,
            CREATE_DIRECTORY,
            url_addition=self.directory_to_url_path(path)
        )
        return response.status_code == 200 or response.status_code == 409

    def list_directory(self, path, depth=None):
        """
        Get directory file tree
        :param pentaho: the directory tree
        :return: success/failure
        :rtype: list
        """
        dir_tree = []
        url_addition = "{}/tree".format(self.directory_to_url_path(path))
        if type(depth) is int:
            url_addition = "{}?depth={}".format(url_addition, depth)
        response = self._pentaho.make_call(
            PENTAHO_FILES_ENDPOINT_API,
            LIST_DIRECTORY,
            url_addition=url_addition)
        if response.status_code == 200:
            try:
                dir_tree = xmltodict.parse(response.text)['repositoryFileTreeDto']
            except Exception, e:
                logger.exception(e)
        return dir_tree

    def get_acl(self, path):
        """
        Get ACL for a specific path/file
        :param path: path to get ACL
        :return: dict with ACL parameters
        """
        url_addition = "{}/acl".format(self.directory_to_url_path(path))
        response = self._pentaho.make_call(
            PENTAHO_FILES_ENDPOINT_API,
            GET_ACL,
            url_addition=url_addition)
        acl = False
        if response.status_code == 200:
            try:
                acl = xmltodict.parse(response.text)['repositoryFileAclDto']
            except Exception, e:
                logger.exception(e)
        return acl

    def set_acl(self, path, permissions):
        """
        Set ACL for a specific path/file
        :param path: path to set ACL
        :param permissions: dict with ACL parameters format
                Example of permission dictionnary:
                {
                    "entriesInheriting": False,
                    "owner": "test@test.com",
                    "ownerType": "1",
                    "aces": [
                        {
                            "modifiable": True,
                            "recipientType": 1,
                            "permissions": [ 0 ],
                            "recipient": "Authenticated"
                        },
                        {
                            "modifiable": True,
                            "recipientType": 1,
                            "permissions": [ 4 ],
                            "recipient": "Administrator"
                        }
                    ]
                }
        :return: boolean true/false if operation succeeded
        """
        url_addition = "{}/acl".format(self.directory_to_url_path(path))
        response = self._pentaho.make_call(
            PENTAHO_FILES_ENDPOINT_API,
            SET_ACL,
            url_addition=url_addition,
            json=permissions
        )
        return response.status_code == 200

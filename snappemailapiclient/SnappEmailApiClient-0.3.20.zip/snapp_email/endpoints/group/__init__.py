from .Group_17Endpoint import Group_17Endpoint
from .GroupLeave_22Endpoint import GroupLeave_22Endpoint


class GroupEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def Group_17(self):
        """
        :return: Group_17Endpoint
        """
        return Group_17Endpoint(self._api_client)
        
    @property
    def GroupLeave_22(self):
        """
        :return: GroupLeave_22Endpoint
        """
        return GroupLeave_22Endpoint(self._api_client)
        
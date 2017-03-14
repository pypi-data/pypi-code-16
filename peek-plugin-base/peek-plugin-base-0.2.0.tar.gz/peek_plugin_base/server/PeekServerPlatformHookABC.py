from abc import abstractproperty, abstractmethod
from typing import Optional

from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFrontendHookABC import PeekPlatformFrontendHookABC


class PeekServerPlatformHookABC(PeekPlatformCommonHookABC, PeekPlatformFrontendHookABC):
    @abstractproperty
    def dbConnectString(self) -> str:
        """ DB Connect String

        :return: The SQLAlchemy database engine connection string/url.

        """

    @abstractmethod
    def getOtherPluginStorageApi(self, pluginName:str) -> Optional[object]:
        """ Get Other Plugin Storage Api

        Asks the plugin for it's Storage api object and return it to this plugin.
        The API returned matches the platform service.

        :param pluginName: The name of the plugin to retrieve the API for
        :return: An instance of the other plugins Storage API on the server service

        """

from typing import Optional

from peek_platform import PeekPlatformConfig
from peek_plugin_base.client.PeekClientPlatformHookABC import PeekClientPlatformHookABC


class PeekClientPlatformHook(PeekClientPlatformHookABC):
    def getOtherPluginApi(self, pluginName: str) -> Optional[object]:
        pluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = pluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.client.PluginClientEntryHookABC import \
            PluginClientEntryHookABC
        assert isinstance(otherPlugin, PluginClientEntryHookABC), (
            "Not an instance of PluginClientEntryHookABC")

        return otherPlugin.publishedClientApi

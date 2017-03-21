from typing import Optional

from peek_platform import PeekPlatformConfig
from peek_plugin_base.agent.PeekAgentPlatformHookABC import PeekAgentPlatformHookABC


class PeekAgentPlatformHook(PeekAgentPlatformHookABC):
    def getOtherPluginApi(self, pluginName: str) -> Optional[object]:
        pluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = pluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
        assert isinstance(otherPlugin, PluginAgentEntryHookABC), (
            "Not an instance of PluginAgentEntryHookABC")

        return otherPlugin.publishedAgentApi

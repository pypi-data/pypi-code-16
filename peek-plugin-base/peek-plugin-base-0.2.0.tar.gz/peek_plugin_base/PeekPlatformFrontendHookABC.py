from abc import ABCMeta

from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource


class PeekPlatformFrontendHookABC(metaclass=ABCMeta):
    def __init__(self):
        self.__rootResource = FileUnderlayResource()

    def addStaticResourceDir(self, dir: str) -> None:
        self.__rootResource.addFileSystemRoot(dir)

    def addResource(self, pluginSubPath: bytes, resource: BasicResource) -> None:
        pluginSubPath = pluginSubPath.strip(b'/')
        self.__rootResource.putChild(pluginSubPath, resource)

    @property
    def rootResource(self) -> BasicResource:
        return self.__rootResource

import os

from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from peek_platform import PeekPlatformConfig

root = FileUnderlayResource()

def setup():
    # Setup properties for serving the site
    root.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_mobile
    frontendProjectDir = os.path.dirname(peek_mobile.__file__)
    distDir = os.path.join(frontendProjectDir, 'build-web', 'dist')

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    root.addFileSystemRoot(distDir)

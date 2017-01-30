from notebook.services.contents.filemanager import FileContentsManager
from traitlets import Any


class HookFileContentsManager(FileContentsManager):
    """Local spawner that runs single-user servers as the same user as the Hub itself.

    Overrides user-specific env setup with no-ops.
    """

    pre_get_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called before getting a notebook.
        """
    )

    post_get_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called after getting a notebook.
        """
    )

    pre_update_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called before update a notebook.
        """
    )

    post_update_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called after update a notebook.
        """
    )

    pre_delete_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called before delete a notebook.
        """
    )

    post_delete_hook = Any(None, config=True,
        help="""Python callable thereof
        to be called after delete a notebook.
        """
    )

    def get(self, path, content=True, type=None, format=None):
        if self.pre_get_hook:
            self.pre_get_hook(path=path, content=content, type=type, format=format, contents_manager=self)
        returned = super(HookFileContentsManager, self).get(path, content, type, format)
        if self.post_get_hook:
            self.post_get_hook(path=path, content=content, type=type, format=format, contents_manager=self)
        return returned

    def update(self, model, path):
        if self.pre_update_hook:
            self.pre_update_hook(model=model, path=path, contents_manager=self)
        returned = super(HookFileContentsManager, self).update(model, path)
        if self.post_update_hook:
            self.post_update_hook(model=model, path=path, contents_manager=self)
        return returned

    def delete(self, path):
        if self.pre_delete_hook:
            self.pre_delete_hook(path=path, contents_manager=self)
        returned = super(HookFileContentsManager, self).delete(path)
        if self.post_delete_hook:
            self.post_delete_hook(path=path, contents_manager=self)
        return returned

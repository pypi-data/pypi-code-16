from wizards.storage.session import SessionManager


class SQLRepository(SessionManager):
    """A mixin class for :class:`ea.ddd.Repository` implementations
    that sets up and tears down a :class:`sqlalchemy.orm.Session`
    when the repository is invoked as a context guard.
    """
    dsn = None
    DoesNotExist = type('DoesNotExist', (Exception,), {})

    @SessionManager.with_session
    def persist(self, *args, **kwargs):
        return super(SQLRepository, self).persist(*args, **kwargs)

    def enter(self, *args, **kwargs):
        self._local.depth += 1
        if self._local.depth > 0:
            self.session.begin_nested()

        return self.session

    def exit(self, cls, exc, tb):
        assert self._factory is not None
        self._local.depth -= 1
        if cls is None:
            self.session.commit()
        if self._local.depth == -1:
            self.factory.remove()
            self._local.session = None

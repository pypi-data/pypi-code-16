"""
    authorization.map
    ~~~~~~~~~~~~~~~~~
"""
import collections.abc
import contextlib
import logging
import psycopg2
import authorization_levels

_logger = logging.getLogger(__name__)

_valid_levels = {getattr(authorization_levels, l) for l in dir(authorization_levels) if l[:6] == 'LEVEL_' and l != 'LEVEL_DEFAULT'}

_q_crt_user_authz = """
    CREATE TABLE IF NOT EXISTS user_authz (
        username text PRIMARY KEY,
        authz_level integer DEFAULT 0
    );"""
_q_crt_user_authz_auditlog = """
    CREATE TABLE IF NOT EXISTS user_authz_audit (
        username text,
        authz_level integer,
        ts timestamp without time zone DEFAULT (now() at time zone 'utc'),
        active boolean
    );"""
_q_log_change = """
    INSERT INTO user_authz_audit (
        username, authz_level, active
    ) VALUES(%s, %s, %s);"""
_q_upd_authz_level = "UPDATE user_authz SET authz_level=%s WHERE username=%s"
_q_ins_user = "INSERT INTO user_authz (username, authz_level) VALUES(%s, %s)"
_q_sel_authz_level = "SELECT authz_level from user_authz WHERE username=%s"
_q_sel_all = "SELECT username FROM user_authz"
_q_del_user = "DELETE FROM user_authz WHERE username=%s"
_q_cnt_all = "SELECT COUNT(*) FROM user_authz"


class AuthzMap(collections.abc.MutableMapping):
    """ A MutableMapping, mapping usernames to authorization levels, backed by
    Postgres.

    See :func:`psycopg2.connect` for constructor arguments.

    Usage:

    ::

        import authorization
        import authorization_levels  # from datapunt-authorization-levels

        authzmap = authorization.AuthzMap(**psycopgconf)

        if authzmap['myuser'] == authorization_levels.LEVEL_EMPLOYEE:
            ...  # do some eployee-e things

    """

    def __init__(self, *args, **kwargs):
        self._conn = psycopg2.connect(*args, **kwargs)
        self._conn.autocommit = True

    @contextlib.contextmanager
    def _transaction(self):
        """ Convenience contextmanager for transactions.
        """
        with self._conn:
            with self._conn.cursor() as cur:
                yield cur

    def create(self):
        """ Create the tables for authz.
        """
        with self._transaction() as cur:
            cur.execute(_q_crt_user_authz)
            if cur.rowcount > 0:
                _logger.info("Authz user tables created")
            cur.execute(_q_crt_user_authz_auditlog)
            if cur.rowcount > 0:
                _logger.info("Authz auditlog tables created")

    def __setitem__(self, username, authz_level):
        """ Assign the given permission to the given user and log the action in
        the audit log.
        """
        if authz_level not in _valid_levels:
            raise ValueError()
        try:
            cur_authz_level = self[username]
            if authz_level == cur_authz_level:
                return
            q = (_q_upd_authz_level, (authz_level, username))
        except KeyError:
            q = (_q_ins_user, (username, authz_level))
        with self._transaction() as cur:
            cur.execute(*q)
            cur.execute(_q_log_change, (username, authz_level, True))

    def __getitem__(self, username):
        """ Get the current authorization level for the given username.
        """
        with self._conn.cursor() as cur:
            cur.execute(_q_sel_authz_level, (username,))
            result = cur.fetchone()
        if not result:
            raise KeyError()
        return result[0]

    def __delitem__(self, username):
        """ Remove the given user from the authz table and log the action in
        the audit log.
        """
        cur_authz_level = self[username]
        with self._transaction() as cur:
            cur.execute(_q_del_user, (username,))
            cur.execute(_q_log_change, (username, cur_authz_level, False))

    def __iter__(self):
        """ Iterate over all username => authz_levels currently in the table.
        """
        with self._conn.cursor() as cur:
            cur.execute(_q_sel_all)
            for username in cur:
                yield username[0]

    def __len__(self):
        """ Number of usernames in the authz table.
        """
        with self._conn.cursor() as cur:
            cur.execute(_q_cnt_all)
            return cur.fetchone()[0]

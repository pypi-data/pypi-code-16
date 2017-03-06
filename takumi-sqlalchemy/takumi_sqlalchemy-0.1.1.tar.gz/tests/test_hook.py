# -*- coding: utf-8 -*-

import mock
import pytest
import sys


@pytest.fixture
def mock_psycogreen():
    mock_patch = mock.Mock()
    mock_gevent = mock.Mock(patch_psycopg=mock_patch)
    mock_green = mock.Mock(gevent=mock_gevent)
    with mock.patch.dict(sys.modules, {
            'psycogreen': mock_green, 'psycogreen.gevent': mock_gevent}):
        yield mock_patch


def test_db_hook_mysql(mock_config, mock_psycogreen):
    from takumi_sqlalchemy import patch_psycopg_hook
    mock_config.settings['DB_SETTINGS'] = {
        'test': {
            'dsn': {
                'master': 'mysql+pymysql://localhost/dev',
                'slave': 'mysql+pymysql://localhost/dev'
            }
        }
    }
    patch_psycopg_hook()
    mock_psycogreen.assert_not_called()


def test_db_hook_psycopg(mock_config, mock_psycogreen):
    from takumi_sqlalchemy import patch_psycopg_hook
    mock_config.settings['DB_SETTINGS'] = {
        'test': {
            'dsn': {
                'master': 'postgresql+psycopg2://localhost/dev',
                'slave': 'postgresql+psycopg2://localhost/dev'
            }
        }
    }
    patch_psycopg_hook()
    mock_psycogreen.assert_called_with()


def test_timeout_hook(mock_config, monkeypatch):
    from takumi_sqlalchemy import timeout_hook
    from takumi.service import ServiceHandler, ApiMap, Context
    from sqlalchemy.orm.session import Session
    from thriftpy.thrift import TApplicationException
    import gevent

    mock_config.thrift_file = 'tests/test.thrift'
    app = ServiceHandler('TestService', hard_timeout=1)
    app.use(timeout_hook)

    @app.api
    def timeout_api():
        gevent.sleep(2)

    mock_invalidate = mock.Mock()
    monkeypatch.setattr(Session, 'invalidate', mock_invalidate)

    api_map = ApiMap(app, Context({'client_addr': 'localhost', 'meta': {}}))
    with pytest.raises(TApplicationException) as exc:
        api_map.timeout_api()
    assert '1 second' in str(exc.value)
    mock_invalidate.assert_called_with()

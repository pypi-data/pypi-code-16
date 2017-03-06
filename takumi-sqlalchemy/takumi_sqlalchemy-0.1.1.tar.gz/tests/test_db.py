# -*- coding: utf-8 -*-

import mock


def test_normilize_dsn(mock_config):
    from takumi_sqlalchemy.utils import normalize_dsn
    sample = 'postgresql+psycopg2://localhost/dev'
    dsn = normalize_dsn(sample)
    assert dsn == {
        'slave': 'postgresql+psycopg2://localhost/dev',
        'master': 'postgresql+psycopg2://localhost/dev'
    }

    sample = {
        'master': 'postgresql+psycopg2://localhost/dev',
        'slave': 'postgresql+psycopg2://localhost/dev_slave',
    }
    dsn = normalize_dsn(sample)
    assert dsn is sample


def test_create_session(mock_config, monkeypatch):
    import takumi_sqlalchemy.database

    mock_session = mock.Mock()
    mock_sessionmaker = mock.Mock(return_value=mock_session)
    monkeypatch.setattr(takumi_sqlalchemy.database, 'sessionmaker',
                        mock_sessionmaker)
    mock_scoped_session = mock.Mock()
    monkeypatch.setattr(takumi_sqlalchemy.database, 'scoped_session',
                        mock_scoped_session)
    mock_engine = 'engine'
    mock_create_engine = mock.Mock(return_value=mock_engine)
    monkeypatch.setattr(takumi_sqlalchemy.database, 'create_engine',
                        mock_create_engine)

    mock_config.settings['DB_POOL_SIZE'] = 50
    conf = {
        'dsn': {
            'master': 'sqlite:///:memory:',
            'slave': 'sqlite:///:memory:',
        },
    }

    from takumi_sqlalchemy.database import _create_session
    from takumi_sqlalchemy.routing import RoutingSession
    _create_session(conf)
    mock_scoped_session.assert_called_with(mock_session)
    mock_sessionmaker.assert_called_with(
        class_=RoutingSession,
        engines={'slave': 'engine', 'master': 'engine'},
        expire_on_commit=False)
    mock_create_engine.assert_called_with(
        'sqlite:///:memory:', pool_recycle=1200, pool_size=50)


def test_session_map(mock_config):
    from takumi_sqlalchemy.database import _session_map
    mock_config.settings['DB_SETTINGS'] = {
        'test_db1': {
            'dsn': 'sqlite:///:memory:',
            'pool_size': 30,
        },
        'test_db2': {
            'dsn': 'sqlite:///:memory:',
            'pool_size': 20,
        }
    }
    session_map = _session_map()
    assert list(sorted(session_map.keys())) == ['test_db1', 'test_db2']


def test_db(mock_config):
    from takumi_sqlalchemy import db
    db.session_map = None
    mock_config.settings['DB_SETTINGS'] = {
        'test_db1': {
            'dsn': 'sqlite:///:memory:',
            'pool_size': 30,
        },
        'test_db2': {
            'dsn': 'sqlite:///:memory:',
            'pool_size': 20,
        }
    }
    assert db['test_db1'] == db.session_map['test_db1']()
    assert db['test_db2'] == db.session_map['test_db2']()


def test_db_query(mock_config):
    from takumi_sqlalchemy import db
    db.session_map = None
    mock_config.settings['DB_SETTINGS'] = {
        'test_db': {'dsn': 'sqlite:///:memory:'}
    }
    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'user'

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(255))

        def as_dict(self):
            return {'id': self.id, 'name': self.name}

    Base.metadata.create_all(bind=db['test_db'].engines['master'])

    with db['test_db'] as session:
        user1 = User(name='hello')
        user2 = User(name='world')
        session.add(user1)
        session.add(user2)
        session.commit()

    users = db['test_db'].using_bind('master').query(User).all()
    assert [u.as_dict() for u in users] == [
        {'name': 'hello', 'id': 1},
        {'name': 'world', 'id': 2}
    ]

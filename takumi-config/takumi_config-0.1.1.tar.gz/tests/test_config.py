import os
import mock
from takumi_config.loader import YamlLoader, Config
from takumi_config._env import EnvConfig
from takumi_config._app import AppConfig


def test_loader():
    loader = YamlLoader('tests/app.yaml')
    assert loader.load() == {
        'name': 'echo',
        'settings': 'tests.settings',
        'app': 'echo:service',
        'thrift_file': 'echo/echo.thrift',
        'requirements': 'requirements.txt',
        'thrift_protocol_class': 'tests.settings.DemoClass',
    }


def test_config_base():
    conf = Config('tests/app.yaml')
    assert conf.get('name') == 'echo'

    with mock.patch.object(YamlLoader, 'load',
                           return_value={'app': 'test-app'}) as mock_loader:
        assert conf.get('app') == 'echo:service'
    mock_loader.assert_not_called()

    # get other config
    assert conf.get('hello') is None


def test_env_config():
    with mock.patch.dict(os.environ, {'TAKUMI_CONFIG_PATH': 'tests/env.yaml'}):
        config = EnvConfig()
    assert config.env == 'prod'


def test_app_config():
    from .settings import DemoClass
    with mock.patch.dict(os.environ,
                         {'TAKUMI_APP_CONFIG_PATH': 'tests/app.yaml'}):
        config = AppConfig()
    assert config.app == 'echo:service'
    assert config.name == 'echo'
    assert config.requirements == 'requirements.txt'
    assert config.thrift_protocol_class is DemoClass


def test_app_config_settings():
    with mock.patch.dict(os.environ,
                         {'TAKUMI_APP_CONFIG_PATH': 'tests/app.yaml'}):
        config = AppConfig()
    assert config.settings == {}
    assert (config.settings['DB_DSN'] ==
            'psycopg2+postgresql://root:123@localhost:5432/dev')

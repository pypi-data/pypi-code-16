import atexit
import json
import logging.config
import os
import sys
import time

import schedule
from NucleusUtils.events import Event
from NucleusUtils.singleton import Singleton
from NucleusUtils.translations.advanced import AdvancedTranslator

from NucleusApp import VERSION
from NucleusApp.chest import Chest
from NucleusApp.config import SettingsManager
from NucleusApp.middlewares.registry import MiddlewareRegistry
from NucleusApp.modules.registry import AppsRegistry

APPLICATION = 'app'
SETTINGS = 'settings'
REGISTRY = 'registry'
MIDDLEWARES = 'middlewares'
SCHEDULE = 'schedule'
TRANSLATOR = 'translator'


class Application(metaclass=Singleton):
    """
    Main application Superclass
    """

    # Override this fields in your subclass
    name = ''
    version = VERSION
    settings_module = 'settings'
    logging_config = 'logging.json'
    locales_path = 'locales'
    modules = []
    middlewares = []

    # Base application logger
    log = logging.getLogger('NucleusApp')

    def __init__(self):
        self.ready = False
        self.translator = AdvancedTranslator(self.locales_path)
        self.schedule = schedule.Scheduler()
        self.set_logging()

    def prepare(self):
        """
        You can override this method
        It will be running before loading modules
        :return:
        """
        pass

    def run(self):
        """
        You can override this method
        It will be called after loading modules and settings
        :return:
        """
        pass

    @property
    def description(self):
        """
        Get description of application from pydoc
        :return:
        """
        return self.__doc__ or ''

    @description.setter
    def description(self, value):
        self.__doc__ = value

    @property
    def path(self):
        """
        Base application path
        :return:
        """
        return get_base_dir()

    def about(self):
        return "{} v{} - {}".format(self.name, self.version, self.description)

    def setup(self):
        """
        Prepare application for work.
        Load settings and all installed modules
        :return:
        """
        if not self.ready:
            # Add application to root container of Chest
            Chest().root[APPLICATION] = self
            Chest().root[SETTINGS] = self.settings
            Chest().root[REGISTRY] = self.registry
            Chest().root[MIDDLEWARES] = self.middleware
            Chest().root[SCHEDULE] = self.schedule
            Chest().root[TRANSLATOR] = self.translator

            # Prevent to remove app from Chest
            Chest().root.lock_fields(APPLICATION, SETTINGS, REGISTRY, MIDDLEWARES, SCHEDULE, TRANSLATOR)

            self.settings.load(self.settings_module)

            self.translator.default_locale = self.settings.get('DEFAULT_LOCALE', None)

            # Call custom `.prepare()` method
            self.prepare()

            if not self.middleware.ready:
                self.middleware.populate(self.middlewares)

            if not self.registry.ready:
                self.registry.populate(self.modules)

            # Trigger on_ready event
            self.ready = True
            self.on_ready.trigger()

            # Call custom `.run()` method
            self.run()

            self.log.debug('Application is loaded!')

            self.run_schedule_pending()

        return self

    def start(self):
        return self.setup()

    def run_schedule_pending(self):
        try:
            self.log.debug('Scheduler is running')
            while True:
                self.schedule.run_pending()
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.log.debug('Scheduler is stopped')

    def set_logging(self):
        # https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
        config_file = os.path.abspath(self.logging_config)
        if os.path.exists(config_file):
            mime = config_file.rpartition('.')[2]
            with open(config_file, 'rt') as file:
                if mime == 'json':
                    logging_config = json.load(file)
                elif mime in ['yml', 'yaml']:
                    # TODO: load from yaml
                    logging_config = {}
                else:
                    raise TypeError('Unknown config file format!')
                logging.config.dictConfig(logging_config)
        else:
            logging.basicConfig(level=logging.DEBUG)

    def __init_subclass__(cls, **kwargs):
        # Register events
        cls.on_init = Event(name=cls.name + ':on_init')
        cls.on_exit = Event(name=cls.name + ':on_exit')
        cls.on_ready = Event(name=cls.name + ':on_ready')

        # Register SystemExit event
        atexit.register(cls.on_exit)

        # Load settings from settings module
        cls.settings = SettingsManager()

        # Load external modules and middlewares
        cls.registry = AppsRegistry(cls, None)
        cls.middleware = MiddlewareRegistry(cls, None)

        super().__init_subclass__(**kwargs)
        cls.ready = False

        # Trigger on_init event
        cls.on_init()

    def __str__(self):
        return 'Application:' + self.name


def get_base_dir():
    """
    Get base application directory
    :return:
    """
    return os.path.dirname(os.path.abspath(sys.modules.get('__main__').__file__))


class Manager:
    @classmethod
    def get_app(cls) -> Application:
        return Chest().root[APPLICATION]

    @property
    def app(self) -> Application:
        return self.get_app()

    def __enter__(self) -> Application:
        return self.get_app()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

import logging
import datetime

from kore.components.plugins.base import BasePluginComponent

log = logging.getLogger(__name__)


class TestPlugin(BasePluginComponent):

    def get_factories(self):
        return (
            (self.test_factory.__name__, self.test_factory),
        )

    def get_services(self):
        return (
            (self.test_service.__name__, self.test_service),
        )

    def pre_hook(self, container):
        log.debug("Test Pre Hooked")

    def test_factory(self, container):
        return datetime.datetime.utcnow()

    def test_service(self, container):
        return datetime.datetime.utcnow()

    def post_hook(self, container):
        log.debug("Test Post Hooked")

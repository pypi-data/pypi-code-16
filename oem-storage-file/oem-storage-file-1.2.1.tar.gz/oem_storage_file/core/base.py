from oem_framework.plugin import Plugin

import logging
import os

log = logging.getLogger(__name__)


class BaseFileStorage(Plugin):
    def database_path(self, source, target):
        # Retrieve package path
        package_path = self.package_path(source, target)

        if package_path is None:
            log.warn('Unknown database name for source %r, target %r', source, target)
            return None

        # Retrieve database name
        database_name = self._client.database_name(source, target)

        if database_name is None:
            log.warn('Unknown database name for source %r, target %r', source, target)
            return None

        # Build collection path
        return os.path.join(package_path, database_name)

    def package_path(self, source, target):
        name = self._client.package_name(source, target)

        if name is None:
            return None

        return os.path.join(self.main.path, name)

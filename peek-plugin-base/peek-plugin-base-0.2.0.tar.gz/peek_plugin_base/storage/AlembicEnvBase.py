from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.dialects.postgresql.base import PGDialect
from txhttputil.util.LoggingUtil import setupLogging


class AlembicEnvBase:
    def __init__(self, targetMetadata):
        setupLogging()

        self._config = context.config
        self._targetMetadata = targetMetadata
        self._schemaName = targetMetadata.schema

    def _includeObjectFilter(self, object, name, type_, reflected, compare_to):
        # If it's not in this schema, don't include it
        if hasattr(object, 'schema') and object.schema != self._schemaName:
            return False

        return True

    def run(self):
        """Run migrations in 'online' mode.
    
        In this scenario we need to create an Engine
        and associate a connection with the context.
    
        """
        connectable = engine_from_config(
            self._config.get_section(self._config.config_ini_section),
            prefix='sqlalchemy.',
            poolclass=pool.NullPool)

        with connectable.connect() as connection:
            # Ensure the schema exists
            if isinstance(connection.dialect, MSDialect):
                connection.execute(
                    "IF(SCHEMA_ID('%s')IS NULL) BEGIN EXEC('CREATE SCHEMA [%s]')END" % (
                        self._schemaName, self._schemaName))

            elif isinstance(connection.dialect, PGDialect):
                connection.execute(
                    'CREATE SCHEMA IF NOT EXISTS "%s" ' % self._schemaName)

            else:
                raise Exception('unknown dialect %s' % connection.dialect)

            context.configure(
                connection=connection,
                target_metadata=self._targetMetadata,
                include_object=self._includeObjectFilter,
                include_schemas=True,
                version_table_schema=self._schemaName
            )

            with context.begin_transaction():
                context.run_migrations()

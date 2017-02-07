from groundwork_validation.patterns import GwDbValidatorsPattern


class GwDbValidator(GwDbValidatorsPattern):

    def __init__(self, app, **kwargs):
        self.name = self.__class__.__name__
        super(GwDbValidator, self).__init__(app, **kwargs)

    def activate(self):
        self.signals.connect(receiver="db_validation_setup",
                             signal="db_class_registered",
                             function=self._setup_db_validation,
                             description="Setups the validations checks for newly registered database classes")

    def deactivate(self):
        pass

    def _setup_db_validation(self, plugin, *args, **kwargs):
        database = kwargs.get("database", None)
        db_class = kwargs.get("db_class", None)

        if database is None or db_class is None:
            return

        # We must not validate our own hash database tables.
        # If we do so, this would lead to an infinity loop.
        if database.name == "hash_db":
            return

        self.validators.db.register(name="%s_db_validator" % db_class.name,
                                    description="Database validator for %s" % db_class.name,
                                    db_class=db_class)

class Authorizations(object):
    _default_action = "deny"
    """
    Authorizations base class.
    Developper must inherit this class to create its own rules.

    Example:
        class AdminAuthorizations(Authorizations):
            def can_view_project(self, project_id):
                return True
    """
    def __init__(self, default_action="deny"):
        """
        Args:
            default_action (str): default action taken if access method is not defined (allow or deny)
        """
        if default_action not in ("deny", "allow"):
            raise ValueError("'{0}' is not a valid action, 'deny' and 'allow' are.".format(default_action))
        self._default_action = default_action

    def generate_error(self, rule, kwargs):
        """ Build an error when access defined by rule is not granted
        Args:
            rule (Rule): an access rule
            kwargs (dict): args received when asking for authorization
        Returns:
            Exception: exception raised by Ability if access is not granted
        """
        return Exception("Access denied for {0} ({1})".format(rule.name, kwargs))

    def __getattr__(self, name):
        """
        Returns the default action for every undefined 'rule' methods (the one beginning with 'can_*').
        If `name` does not match the rule method name pattern it calls super()
        Args:
            name (str): attribute name

        Returns:
            function: default action
        Raises:
            AttributeError: if not accessing a 'rule' method
        """
        if name.startswith("can_"):
            return self._deny if self._default_action == "deny" else self._allow
        else:
            super().__getattr__(name)

    def _deny(self, *args, **kwargs):
        return False

    def _allow(self, *args, **kwargs):
        return True

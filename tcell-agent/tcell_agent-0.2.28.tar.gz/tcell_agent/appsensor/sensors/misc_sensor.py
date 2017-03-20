import traceback

from tcell_agent.appsensor.sensor import send_event


class MiscSensor(object):
    def __init__(self, policy_json=None):
        self.csrf_exception_enabled = False
        self.sql_exception_enabled = False
        self.excluded_route_ids = {}

        if policy_json is not None:
            self.csrf_exception_enabled = policy_json.get("csrf_exception_enabled", False)
            self.sql_exception_enabled = policy_json.get("sql_exception_enabled", False)

            for route_id in policy_json.get("exclude_routes", []):
                self.excluded_route_ids[route_id] = True

    def csrf_rejected(self, appsensor_meta, reason):
        if not self.csrf_exception_enabled:
            return

        if self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return False

        send_event(appsensor_meta, "excsrf", None, None)

    def sql_exception_detected(self, database, appsensor_meta, exc_type, exc_value, tb):
        if not self.sql_exception_enabled:
            return

        if self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return False

        programming_error = getattr(database, "ProgrammingError")
        operational_error = getattr(database, "OperationalError")
        if not issubclass(exc_type, programming_error) and not issubclass(exc_type, operational_error):
            return

        send_event(appsensor_meta, "exsql", exc_type.__name__, None, payload=traceback.print_tb(tb))

    def __str__(self):
        return "<%s csrf_exception_enabled: %s sql_exception_enabled: %s>" % \
               (type(self).__name__, self.csrf_exception_enabled, self.sql_exception_enabled)

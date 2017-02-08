class Options(object):
    """
    Available options
    """

    def __init__(self, options=None):
        self.options = options

    def get_option(self, option):
        """
        Gets an option if present, else return None
        """
        if hasattr(self, option):
            return getattr(self, option)
        return None

    UPDATE = 'update'
    REMOVE = 'remove'
    PUBLISH = 'publish'
    FROM_TASK = 'from_task'
    PROCESS = 'process'
    STOP_BEFORE = 'stop_before'
    STOP_AFTER = 'stop_after'
    FROMSCRATCH = 'fromscratch'

class Utils(object):

    @staticmethod
    def set_args(parser):
        parser.add_argument('--last-log', dest="lastlog", action="store_true", default=False, help="Get last logs for bank")
        parser.add_argument('--tail', dest="tail", help="number of lines to tail")
        parser.add_argument('--about-me', dest="aboutme", action="store_true", help="Get my user info")
        parser.add_argument('--whatsup', dest="whatsup", action="store_true", default=False, help="Get biomaj info on what biomaj is doing")
        parser.add_argument('--user-login', dest="userlogin", help="Credentials login")
        parser.add_argument('--user-password', dest="userpassword", help="Credentials password")
        parser.add_argument('--proxy', dest="proxy", help="Biomaj daemon URL")  # http://127.0.0.1
        parser.add_argument('--api-key', dest="apikey", help="User API Key")
        parser.add_argument('--update-status', dest="updatestatus", action="store_true", default=False, help="Get update status")
        parser.add_argument('--update-cancel', dest="updatecancel", action="store_true", default=False, help="Cancel current bank update")
        parser.add_argument('--trace', dest="trace", action="store_true", help="Trace operation in zipkin")

        parser.add_argument('-c', '--config', dest="config", help="Configuration file")
        parser.add_argument('--check', dest="check", help="Check bank property file", action="store_true", default=False)
        parser.add_argument('-u', '--update', dest="update", help="Update action", action="store_true", default=False)
        parser.add_argument('--fromscratch', dest="fromscratch", help="Force a new cycle update", action="store_true", default=False)
        parser.add_argument('-z', '--from-scratch', dest="fromscratch", help="Force a new cycle update", action="store_true", default=False)
        parser.add_argument('-p', '--publish', dest="publish", help="Publish", action="store_true", default=False)
        parser.add_argument('--unpublish', dest="unpublish", help="Unpublish", action="store_true", default=False)

        parser.add_argument('--release', dest="release", help="release of the bank")
        parser.add_argument('--from-task', dest="from_task", help="Start cycle at a specific task (init always executed)")
        parser.add_argument('--process', dest="process", help="Linked to from-task, optionally specify a block, meta or process name to start from")
        parser.add_argument('-l', '--log', dest="log", help="log level")
        parser.add_argument('-r', '--remove', dest="remove", help="Remove a bank release", action="store_true", default=False)
        parser.add_argument('--remove-all', dest="removeall", help="Remove all bank releases and database records", action="store_true", default=False)
        parser.add_argument('--remove-pending', dest="removepending", help="Remove pending release", action="store_true", default=False)
        parser.add_argument('-s', '--status', dest="status", help="Get status", action="store_true", default=False)
        parser.add_argument('-b', '--bank', dest="bank", help="bank name")
        parser.add_argument('--owner', dest="owner", help="change owner of the bank")
        parser.add_argument('--stop-before', dest="stop_before", help="Store workflow before task")
        parser.add_argument('--stop-after', dest="stop_after", help="Store workflow after task")
        parser.add_argument('--freeze', dest="freeze", help="Freeze a bank release", action="store_true", default=False)
        parser.add_argument('--unfreeze', dest="unfreeze", help="Unfreeze a bank release", action="store_true", default=False)
        parser.add_argument('-f', '--force', dest="force", help="Force action", action="store_true", default=False)
        parser.add_argument('-h', '--help', dest="help", help="Show usage", action="store_true", default=False)

        parser.add_argument('--search', dest="search", help="Search by format and types", action="store_true", default=False)
        parser.add_argument('--formats', dest="formats", help="List of formats to search, comma separated")
        parser.add_argument('--types', dest="types", help="List of types to search, comma separated")
        parser.add_argument('--query', dest="query", help="Lucene query syntax to search in index")

        parser.add_argument('--show', dest="show", help="Show format files for selected bank", action="store_true", default=False)

        parser.add_argument('-n', '--change-dbname', dest="newbank", help="Change old bank name to this new bank name")
        parser.add_argument('-e', '--move-production-directories', dest="newdir", help="Change bank production directories location to this new path, path must exists")
        parser.add_argument('--visibility', dest="visibility", help="visibility status of the bank")

        parser.add_argument('--maintenance', dest="maintenance", help="Maintenance mode (on/off/status)")

        parser.add_argument('--version', dest="version", help="Show version", action="store_true", default=False)
        parser.add_argument('--status-ko', dest="statusko", help="Get bank in KO status", action="store_true", default=False)

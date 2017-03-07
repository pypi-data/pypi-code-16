import sys

import aalam_common.config as config
from aalam_common.auth import init_auth
from aalam_common.debug import init_debug
from aalam_common.wsgi import WSGIServer


def main():
    init_debug()
    init_auth()
    server = WSGIServer(config.cfg.CONF.app_code)
    server.run()

    # daemontools-encore expects 100 for normal exit
    sys.exit(100)


if __name__ == "__main__":
    main()

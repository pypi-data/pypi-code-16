#!/usr/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'grafana-cassandra','console_scripts','grafana-cassandra'
__requires__ = 'grafana-cassandra'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('grafana-cassandra', 'console_scripts', 'grafana-cassandra')()
    )

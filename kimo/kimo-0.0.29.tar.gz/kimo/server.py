import os
import sys
import json
import psutil

from flask import Flask

from kimo import conf

app = Flask(__name__)


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@app.route("/connections")
def list():
    conns = psutil.net_connections()
    response = []
    for conn in conns:
        process_cmdline = None
        process_name = None
        if conn.pid:
            p = psutil.Process(pid=conn.pid)
            process_cmdline = p.cmdline()
            process_name = p.name()

        response.append({
            'laddr': conn.laddr,
            'raddr': conn.raddr,
            'process': {
                'pid': conn.pid,
                'name': process_name,
                'cmdline': process_cmdline,
            }
        })

    return json.dumps(response)


def main():
    app.debug = True
    app.run(host='0.0.0.0', port=conf.KIMO_SERVER_PORT)

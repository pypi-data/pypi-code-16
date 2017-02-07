import os, sys

import wof.flask

curr_folder = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, '%s/../../../' % curr_folder)

import logging
import wof

from odm2_timeseries_dao import Odm2Dao
#import private_config

"""
    python runserver_odm2_timeseries.py
    --config=odm2_config_timeseries.cfg
    --connection=example.connection

"""
#logging.basicConfig(level=logging.DEBUG)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


def startServer(config='odm2_config_timeseries.cfg',connection=None,
                    openPort = 8080):
    dao = Odm2Dao(connection.read())
    app = wof.flask.create_wof_flask_app(dao, config)
    app.config['DEBUG'] = True


    url = "http://127.0.0.1:" + str(openPort)
    print "----------------------------------------------------------------"
    print "Acess Service endpoints at "
    for path in wof.site_map(app):
        print "%s%s" % (url,path)

    print "----------------------------------------------------------------"

    app.run(host='0.0.0.0', port=openPort, threaded=True)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='start WOF for an ODM2 database.')
    parser.add_argument('--config',
                       help='Configuration file', default='odm2_config_timeseries.cfg')
    parser.add_argument('--connection',type=argparse.FileType('r'),
                       help='The name of a file containing the Connection String eg: private.connection which has: mysql://username:password@localhost/database')

    parser.add_argument('--port',
                       help='Open port for server."', default=8080, type=int)
    args = parser.parse_args()
    print(args)

    startServer(config=args.config,connection=args.connection,openPort=args.port)

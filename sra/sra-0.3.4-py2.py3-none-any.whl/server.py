import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import uuid
import os
import sys
import subprocess
import json
import version

from daemon import Daemon
from time import gmtime, strftime
from tornado.options import define, options

define("port", default=8080, help="run on the given port", type=int)
define("host", default="127.0.0.1", help="run on the given host", type=str)
define("secret", help="secret", type=str)
define("daemon", default=False, help="daemon")


def verify_secret_token(token):
    return options.secret == token


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/upload", UploadHandler),
            (r"/_sockets", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('')


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        deploy_to = self.request.headers.get('deploy_to')
        secret = self.request.headers.get('X-Secret-Token')
        upload_to = deploy_to + "tmp/"

        response = {}

        if verify_secret_token(secret):
            file_info = self.request.files['package'][0]
            file_name = file_info['filename']
            extension = os.path.splitext(file_name)[1]
            cname = str(uuid.uuid4()) + extension
            fh = open(upload_to + cname, 'w')
            fh.write(file_info['body'])
            response['deploy_id'] = cname
            response['result'] = True
        else:
            response['result'] = False
            response['message'] = "invalid secret"

        self.write(json.dumps(response))


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        # logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    @classmethod
    def send_status(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    @classmethod
    def close_connection(cls):
        response = {'status': True, 'close': True}
        ChatSocketHandler.send_updates(response)

    def exec_and_print(self, command):
        subprocess.call(command, shell=True)
        response = {'status': True, 'close': False, 'updates': command}
        ChatSocketHandler.send_updates(response)

    def print_and_close(self, message):
        response = {'status': True, 'close': True, 'updates': message}
        ChatSocketHandler.send_updates(response)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)

        shared_paths = parsed['shared_paths']
        deploy_directory = parsed['deploy_to']
        current_directory = deploy_directory + 'current'
        releases_directory = deploy_directory + 'releases/'
        shared_directory = deploy_directory + 'shared/'
        upload_to = deploy_directory + "tmp/"

        secret_token = parsed['secret_token']
        if not verify_secret_token(secret_token):
            self.print_and_close('invalid secret')

        if parsed['task'] == 'deploy':
            latest_release_dir = strftime("%Y%m%d%H%M%S", gmtime())
            latest_release = releases_directory + latest_release_dir

            # unzip /data/www/support.qq.com/tmp/xx.zip -d /data/www/support.qq.com/releases/20160910161839 > /dev/null'
            unzip_command = "unzip " + upload_to + parsed['deploy_id'] + " -d " + latest_release + " > /dev/null"
            self.exec_and_print(unzip_command)

            for item in shared_paths:
                # ln -sF /data/www/support.qq.com/shared/data /data/www/support.qq.com/releases/xxxxx/data
                link_command = "ln -sF " + shared_directory + item + " " + latest_release + "/" + item
                self.exec_and_print(link_command)

            env = "export CURRENT=" + current_directory + " && export RELEASE=" + latest_release + " && "

            if parsed['pre_command']:
                self.exec_and_print(env + parsed['pre_command'])

            # rm -f /data/www/support.qq.com/current
            self.exec_and_print('rm -f ' + current_directory)

            # ln -sF /data/www/support.qq.com/releases/20160910161839 /data/www/support.qq.com/current
            link_command = "ln -sF " + latest_release + " " + current_directory
            self.exec_and_print(link_command)

            # for project custom
            if parsed['post_command']:
                self.exec_and_print(env + parsed['post_command'])

            # print latest release directory name
            self.print_and_close("Latest release is " + latest_release_dir)

        elif parsed['task'] == 'rollback':
            # get all releases directories
            process = subprocess.Popen('ls -At ' + releases_directory, shell=True, stdout=subprocess.PIPE)
            out, err = process.communicate()
            releases = filter(None, out.split("\n"))

            # check if available to rollback
            if len(releases) > 1:
                latest_release = releases_directory + releases[1]
                current_release = releases_directory + releases[0]

                # delete current symlink
                self.exec_and_print('rm -f ' + current_directory)

                link_command = "ln -sF " + latest_release + " " + current_directory
                self.exec_and_print(link_command)

                delete_withdrawn_release = "rm -rf " + current_release
                self.exec_and_print(delete_withdrawn_release)

                self.close_connection()
            else:
                self.print_and_close('No available rollback')

        elif parsed['task'] == 'init':
            self.print_and_close('init feature has not implement')
        elif parsed['task'] == 'check':
            self.print_and_close('check feature has not implement')
        else:
            self.print_and_close('unknown task')


def start_server():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port, options.host)
    tornado.ioloop.IOLoop.current().start()


class SraDaemon(Daemon):
    def run(self):
        start_server()


def main():
    pidfile = '/tmp/srad.pid'

    tornado.options.parse_command_line()
    print "Server started, SRA version:", version.__VERSION__
    print "Listening on " + options.host + ':' + str(options.port)
    print "secret: ", options.secret

    if options.daemon:
        print 'Daemonized'
        daemon = SraDaemon(pidfile)
        daemon.start()
    else:
        try:
            start_server()
        except KeyboardInterrupt:
            sys.exit(0)

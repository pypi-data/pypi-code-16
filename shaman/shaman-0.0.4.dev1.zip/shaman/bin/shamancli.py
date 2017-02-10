import sys
import os
import configparser
import logging
import logging.handlers
import traceback
import signal
import argparse

from multiprocessing import Queue, Process
if os.name == 'nt':
    from signal import SIGTERM
else:
    from signal import SIGTERM,SIGKILL


def spawn_consumer(basepath, worker_config, worker_num, q):
    from shaman.src.consumer import Consumer
    cls = Consumer(basepath, worker_config, worker_num, q)
    cls.run()

class Daemon:
    """
    Daemon is main class of shaman which is used for start|stop|restart workers. It also controls arguments for
    input, demonizing and etc. To get help, please use command:
    
        shaman --help
    """
    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.init_config()
        self.setup_logging()
        self.running = True
        self.workers = []
        self.in_queue = None


    def init_config(self):
        from shaman.src.helpers.daemon_exceptions import SigtermDaemonException
        import shaman.src.abstract_message as abstract_message

        #current_path = [self.basepath + "/" + dir for dir in ("shamanapp",)]

        self.daemon_config = configparser.RawConfigParser()
        self.daemon_config.read(cliArgs.configuration)

        self.number_of_workers = int(self.daemon_config['GENERAL']['num_workers'])
        self.pidfile_path = self.daemon_config['GENERAL']['pidfile_path']

        self.pidfile = "{}/shamand.pid".format(self.pidfile_path)
        self.basepath = self.daemon_config['GENERAL']['basepath']
        sys.path.insert(0, self.basepath+'/shamanapp')
        sys.path.insert(0, self.basepath+'/shamanapp/helpers')
        self.daemon_log = self.daemon_config['GENERAL']['logfile_path']

        #self.basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


        self.abstract_message_module = abstract_message

        self.SigtermDaemonException = SigtermDaemonException

        self.Worker = None

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.exit(1)

        pid = str(os.getpid())
        with open(self.pidfile, "w") as f:
            f.write(pid)
            f.close()

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        self.my_logger.info("Starting...")
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            pid = None
        
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            print(message%self.pidfile)
            self.my_logger.error(message % self.pidfile)
            sys.exit(1)

        if cliArgs.daemon:
            self.daemonize()
            self.my_logger.info("Daemon started.")
        else:
            self.my_logger.info("No daemon mode started")

        def sigint_terminate(signal, frame):
            self._raise_terminate()

        signal.signal(signal.SIGTERM, sigint_terminate)
        signal.signal(signal.SIGINT, sigint_terminate)

        self.run()

    def stop(self):
        self.my_logger.warning("Stopping...")
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            print(message % self.pidfile)
            return

        os.kill(pid, SIGTERM)

    def kill_workers(self):
        self.my_logger.info("Killing all workers.")

        for pid in self.workers:
            try:
                if os.name == 'nt':
                    os.popen('TASKKILL /PID ' +str(pid[0]) + ' /F')
                else:
                    os.kill(int(pid[0]), SIGKILL)
            except OSError as e:
                pass
            self.my_logger.info('Sending SIGTERM signal to pid:{}'.format(int(pid[0])))

        self.join_all_workers()

    def join_all_workers(self):
        for proc in self.workers:
            proc[1].join()
        self.my_logger.info("All workers are shutted down.")

    def restart(self):
        self.my_logger.info("Restarting daemon and all workers...")
        self.stop()
        self.start()

    def parse_config(self, config):
        from shaman.src.helpers.configuration_change import CustomParser
        consumer_config = CustomParser()
        consumer_config.read(config)
        return consumer_config.as_dict()

    def modify_config_according_to_cliargs(self, initial_config, cliArgs):
        from shaman.src.helpers.configuration_change import ignore_after, ignore_fields, is_config_correct

        # if cliArgs.remove_fields is set, then the fields in it will be removed from worker_config (and therefore stages will be removed too)
        if cliArgs.remove_fields:
            fields_to_remove = cliArgs.remove_fields[:]
            initial_config = ignore_fields(initial_config, fields_to_remove)

        if cliArgs.ignore_after:
            after = cliArgs.ignore_after
            initial_config = ignore_after(initial_config, after)

        is_config_correct(initial_config)

        # adding an additional message_printer
        if cliArgs.print_fields:
            order = cliArgs.print_fields[0]
            fields_to_print = cliArgs.print_fields[1:]

            initial_config['STAGES']['message_printer_custom_'] = "'classname': 'MessagePrinterStage'," \
                                                                  "'python_class_filename': 'message_printer'"
            initial_config['message_printer_custom_'] = {'order': int(order),
                                                         'fields_to_print': ",".join(fields_to_print)}


        return initial_config

    def run(self):
        self.my_logger.info("Starting workers")
        self.workers = []

        self.in_queue = Queue(maxsize=self.number_of_workers*2)

        print('Starting workers with basepath {}'.format(self.basepath))

        for worker_num in range(self.number_of_workers):
            print(cliArgs.configuration)

            worker_config = self.parse_config(cliArgs.configuration)
            worker_config = self.modify_config_according_to_cliargs(worker_config, cliArgs)

            p = Process(target=spawn_consumer, args=(self.basepath, worker_config, worker_num, self.in_queue))
            p.start()
            self.workers.append((p.pid, p))

        try:
            self.my_logger.info("All workers started.")
            self.main_cycle()
        except self.SigtermDaemonException as e:
            self.my_logger.info('Stopping')
            self.kill_workers()

            if cliArgs.daemon:
                self.delpid()
            #exit(0)
        except Exception as e:
            self.my_logger.error('Exception in daemon run(): {}'.format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            raise e


    def main_cycle(self):
        if cliArgs.stdin_input:
            current_line_index = 0
            while current_line_index < cliArgs.drop_first:
                current_line_index += 1
                l = sys.stdin.readline()

            for l in sys.stdin:

                if not self.running:
                    break
                self.in_queue.put(l.strip('\n'))
                current_line_index += 1

        else:
            while self.running:
                self.in_queue.put('') # empty line is regular message

        for i in range(self.number_of_workers):
            self.in_queue.put(self.abstract_message_module.control_messages['shutdown'])

        if cliArgs.stdin_input:
            self.my_logger.info('Stopped on stdin line {}'.format(current_line_index))

        self.join_all_workers()
        if cliArgs.daemon:
            self.delpid()

    def _raise_terminate(self, *args):
        if self.running:
            self.running = False
            self.my_logger.info('Shutting down stages')

        # else:
        #     self.my_logger.info('Raising SigtermDaemonException')
        #     raise self.SigtermDaemonException()

    def setup_logging(self):
        # Set up our logger

        self.my_logger = logging.getLogger('Shaman_daemon')
        self.my_logger.setLevel(logging.INFO)

        # Add handler with rotation to the logger
        handler = logging.handlers.RotatingFileHandler(
            self.daemon_log,
            mode='a+',
            maxBytes=20480000, backupCount=5)

        # Set logging format
        log_formatter = logging.Formatter(
            fmt='%(asctime)s:%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(log_formatter)

        # adding handler for logging to file
        self.my_logger.addHandler(handler)


def main():
    cli = argparse.ArgumentParser(
        description='Main shaman module. Use it to start|stop|restart daemon or start non-daemon modes of shaman',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cli.add_argument('command', choices=['stop', 'start', 'restart', ''], help='Command to daemon', nargs="*",
                     default='')

    group = cli.add_mutually_exclusive_group()
    group.add_argument('-i', dest='stdin_input', help='Use stdin input as main input', action='store_true',
                       default=False)
    group.add_argument('-d', dest='daemon', help='Daemonize main process', action='store_true', default=False)

    requiredNamed = cli.add_argument_group('required named arguments')
    cli.add_argument('-c', dest='configuration', type=str,
                     help='Path to configuration file', required=True)

    cli.add_argument('--drop_first', dest='drop_first', help='drop first lines ', action='store', type=int, default=0)

    cli.add_argument('-p', '--print_fields', nargs='+')
    cli.add_argument('-r', '--remove_fields', nargs='+')
    cli.add_argument('--ignore_after', dest='ignore_after', type=int)

    global cliArgs
    cliArgs = cli.parse_args()

    if cliArgs.stdin_input and cliArgs.command:
        print("Argument conflict error: argument -i is not allowed with start|stop|restart command")
        exit(0)

    elif cliArgs.stdin_input:
        cliArgs.command = ["start"]

    try:

        daemon = Daemon()

        logger = daemon.my_logger
        if not cliArgs.command:
            print("No command specified! use --help to check arguments")
            exit(0)

        if cliArgs.command[0] == 'start':
            print("Starting")
            daemon.start()
        elif cliArgs.command[0] == 'stop':
            print('Stopping')
            daemon.stop()
        elif cliArgs.command[0] == 'restart':
            print('Restarting..')
            daemon.restart()

    except ImportError as e:
        print("""****

        Import exception occured on shaman init.
        If your system is Ubuntu, make sure that current source is activated and PYTHONPATH
        environment variable specified. On mac make sure only for PYTHONPATH, there is no env for it.

        For python2 on Ubuntu use these commands before running daemon:
            source /opt/shaman/lib/ext/shaman-env/bin/activate
            export PYTHONPATH=/opt/shaman:$PYTHONPATH

        For python3 on Ubuntu use these commands before running daemon:
            source /opt/shaman/lib/ext/shaman_py3/bin/activate
            export PYTHONPATH=/opt/shaman:$PYTHONPATH

        For start on mac use before running daemon:
            export PYTHONPATH=[shaman dir]:$PYTHONPATH

    *****
    """)
        raise e

    except Exception as e:
        raise e

if __name__=='__main__':
    # Set up catching of SIGTERM and SIGINT signals to proper work with daemon stop routine (send messages on exit, etc)
    main()


"""WORKER.PY

The SimC worker, which registeres the rpc conf['wamp']['rpc_simc_dps'].
When the RPC is called SimC is triggered and the result is returned.

This class can be started multiple times.

Usage:
    callee-publisher.py start [--docker] [--simc_log] [--debug] [--publish_off] [--log_off]
    callee-publisher.py -h | --help

Options:
    -h --help           Show this screen.
    --docker            Activate docker mode: start SimC differently, change encoding, clean up reports dir
    --simc_log          Publish simc console output to ['worker']['topic_simc_log'] (does not include --debug).
    --debug             Output debug messages.
    --log_off           Don't output anything per self.log.info/ .debug.
    --publish_off       Don't output anything per publish.

"""
import simc_autobahn.py_version_check
import sys
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import RegisterOptions
import subprocess
from socket import gethostname
import json
from docopt import docopt
from os import path, makedirs, walk, environ
import timeit
import configparser
from tempfile import TemporaryDirectory
sys.path.append("..")
from simc_autobahn.my_logger import MyLogger

conf = configparser.ConfigParser()
conf.read(path.join(path.dirname(__file__), '..', 'config.ini'))


class MyComponent(ApplicationSession):
    @staticmethod
    def find_simc_exe(simc_exe, start_path='/'):
        """Find SimC executable.

        Note: only returns the first match, if you have mutiple SimC
        installations, you have to adapt the conf file manually.

        Args:
            simc_exe: name of the simc exe to look for
            start_path (str): Path to start looking at (default is '/').

        Returns:
            str: Path where the SimC executable was found.

        """
        def find_filename(fs, name):
            for f in fs:
                if f == name:
                    return f

        for root, dirs, files in walk(start_path):
            file = find_filename(files, simc_exe)
            if file is not None:
                return path.join(root, file)

    def run_simc(self, simc_args, logger):
        """Run SimC

        Args:
            simc_args: arguments for simc in form of an array

        Returns:
            SimC output

        """
        try:
            simc_exe = conf['worker']['simc_exe']
            if len(simc_exe) > 0:
                # let's check if it is correct
                if not path.isfile(simc_exe):
                    raise FileNotFoundError
            else:
                raise KeyError
        except Exception:
            logger.info('SimC not found, searching filesystem ...')
            logger.info('Alternatively you can edit the value conf[worker][simc_exe] in conf.ini')
            if args['--docker']:
                # we are in linux
                simc_exe = self.find_simc_exe('simc')
            else:
                simc_exe = self.find_simc_exe('simc.exe')

            logger.info(f"SimC found at {simc_exe}")
            conf['worker']['simc_exe'] = simc_exe
            with open(path.join(path.dirname(__file__), '..', 'config.ini'), 'w') as configfile:
                conf.write(configfile)

        return subprocess.Popen([simc_exe] + simc_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # MAIN WORKER FUNCTION
    #
    def simc_dps(self, simc_args):
        """Main RPC Method

        Args:
            simc_args: the arguments for SimC in form of an array

        Returns:
            json: data = {
            "hostname": gethostname(),
            "session": self.session,
            "profile": profile,
            "iterations": iterations,
            "dps": dps,
            "items": items
        }

        """
        start = timeit.default_timer()

        # extract profile name from simc_args
        simc_args = simc_args.split(" ")
        profile = simc_args[0].split('=')[1]

        # init logger
        L = MyLogger(f"[{gethostname()}|{self.session}] {profile}", conf['worker']['topic_simc_log'], args, self)

        with TemporaryDirectory() as tmpdirname:
            # we want to also create html reports
            simc_args.append("html=%s" % path.join(tmpdirname, f"{profile}.html"))

            # Run SimC
            L.debug("SimC with %s" % " ".join(simc_args))
            out = self.run_simc(simc_args, L)

            # iterate stdout, extract& log some data
            dps = 'empty'
            iterations = 'empty'
            for line in iter(out.stdout.readline, ''):
                line = line.rstrip()  # remove \n
                if args['--simc_log']:
                    L.info(line)

                try:
                    # dps: comes two times, we want the one which has a number > 0
                    if 'DPS:' in line:
                        if float(line.split()[1]) > 0:
                            dps = line.split()[1]

                    # iterations
                    if "Simulating" in line:
                        iterations = line.split()[2].split('=')[1].strip(',')
                except Exception as e:
                    # we can safely ignore these exceptions, they mostly come from empty/etc lines
                    pass

            # parse reports to get the used items info
            items = []
            encoding = "utf-8" if args['--docker'] else 'ansi'  # let's hope this assumption is true
            html_report = open(path.join(tmpdirname, f"{profile}.html"), 'r', encoding=encoding).read()
            for i, el in enumerate(html_report.splitlines()):
                if "http://www.wowdb.com/items/" in el:
                    items.append(el)

        # return data
        data = {
            "hostname": gethostname(),
            "session": self.session,
            "profile": profile,
            "iterations": iterations,
            "dps": dps,
            "items": items
        }

        stop = timeit.default_timer()
        L.info("SimC done in %ss" % "{:.2f}".format(stop - start))
        return json.dumps(data)

    # ON_JOIN
    #
    def onJoin(self, details):
        self.session = details.session

        l = MyLogger(f"[{gethostname()}|{self.session}]", conf['worker']['topic_simc_log'], args, self)
        l.debug(f"Session ready on {conf['wamp']['uri']}, {conf['wamp']['realm']}")

        # subscribe to topic_keep_alive and listen silently
        def onmsg(count):
            pass
        self.subscribe(onmsg, conf['wamp']['topic_keep_alive'])

        # register simc_dps
        try:
            self.register(self.simc_dps, conf['wamp']['rpc_simc_dps'],
                          RegisterOptions(
                              invoke=u'roundrobin',
                              concurrency=1
                          ))
            l.debug(f"procedure {conf['wamp']['rpc_simc_dps']} registered\n")
        except Exception as e:
            l.error(f"could not register procedure: {e}")


if __name__ == '__main__':
    args = docopt(__doc__)
    runner = ApplicationRunner(url=conf['wamp']['uri'], realm=conf['wamp']['realm'])
    runner.run(MyComponent)

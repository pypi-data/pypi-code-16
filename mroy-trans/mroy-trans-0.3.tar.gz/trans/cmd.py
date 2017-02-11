import sys,argparse,os
from trans.back_query import  brun,srun
from trans.Trans.main import main as mainServer
from qlib.asyn.daemon import run, restart, stop


def get_args():
    DOC = """
    a translation backend .
        mac mode: will use display notification center.
        server mode: will send result to http://localhost:8080/
    """
    parser = argparse.ArgumentParser(usage="how to use this", description=DOC)
    parser.add_argument("-s", "--start", default=False, action="store_true",help="set start")
    parser.add_argument("-k", "--stop", default=False,  action="store_true",help="set stop")
    parser.add_argument("-m", "--mac", default=False, action="store_true", help="set mac mode.")
    # parser.add_argument("-r", "--restart", default=False, action="store_true", help="set restart")
    parser.add_argument("-S", "--Server", default=False, action="store_true", help="set restart")

    return parser.parse_args()


def main():
    args = get_args()
    if args.stop:
        stop(brun)
        stop(srun)
    elif args.Server:
        os.popen("sudo Translate -s").read()
        try:
            mainServer()
        except (InterruptedError, KeyboardInterrupt) as p:
            stop(srun)

    elif args.mac:
        run(brun)
    elif args.start:
        run(srun)
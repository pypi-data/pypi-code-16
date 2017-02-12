import sys,argparse,os
from trans.back_query import  brun,srun,urun
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
    parser.add_argument("-w", "--win", default=False, action="store_true", help="set win mode.")
    # parser.add_argument("-r", "--restart", default=False, action="store_true", help="set restart")

    return parser.parse_args()


def main():
    args = get_args()
    if args.stop:
        if sys.platform != "darwin":
            pass

        else:
            stop(brun)
            stop(srun)

    elif args.mac:
        run(brun)
    elif args.win:
        urun()
    elif args.start:
        if sys.platform != "darwin":
            urun()
        else:
            run(srun)

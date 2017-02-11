import sys,argparse,os
from trans.back_query import  brun
from trans.Trans.main import main



def get_args():
    DOC = """
    a translation backend .
    """
    parser = argparse.ArgumentParser(usage="how to use this", description=DOC)
    parser.add_argument("-s", "--start", default=False, action="store_true",help="set start")
    parser.add_argument("-k", "--stop", default=False,  action="store_true",help="set stop")
    parser.add_argument("-r", "--restart", default=False, action="store_true", help="set restart")
    parser.add_argument("-S", "--Server", default=False, action="store_true", help="set restart")
    return parser.parse_args()


def main():
    args = get_args()
    if args.start:
        run(brun)
    elif args.stop:
        stop(brun)
    elif args.restart:
        restart(brun)
    elif args.Server:
        os.popen("sudo Translate -s").read()
        main()
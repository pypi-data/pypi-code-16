from lib import parse_args
from lib import PrimersGenerator
from list_module import list_sequences


def primers(args):
    """
    """
    pg = PrimersGenerator(args)
    pg.run_pipeline()


def index(args):
    """
    """
    pass


def list_seqs(args):
    """
    """
    list_sequences(args.list_fasta)


def main():
    args = parse_args()
    if args.subparser_name == "primers":
        primers(args)
    elif args.subparser_name == "index":
        index(args)
    else:
        list_seqs(args)

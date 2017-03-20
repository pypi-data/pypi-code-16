import argparse
import os, inspect

# add parent parent path to system path
if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(os.path.dirname(currentdir))
    os.sys.path.insert(0,parentdir)

from camel.modules import call, view, merge, index, statistics, meta, dmr, cluster, pca, annotate, average

def run():
    p = argparse.ArgumentParser(description='Camel')
    subparsers = p.add_subparsers(dest="subcommand")

    # adding alle subparser params

    subp = subparsers.add_parser("call", help="calculate methylation level for each CpG by mapped bam file")
    call.sub(subp)

    subp = subparsers.add_parser("view", help="view the methylation information")
    view.sub(subp)

    subp = subparsers.add_parser("dmr", help="compute differentially methylated regions")
    dmr.sub(subp)

    subp = subparsers.add_parser("merge", help="merge samples")
    merge.sub(subp)

    subp = subparsers.add_parser("index", help="create the index for calling")
    index.sub(subp)

    subp = subparsers.add_parser("statistics", help="compute statistical informations")
    statistics.sub(subp)

    subp = subparsers.add_parser("meta", help="access the meta informations")
    meta.sub(subp)

    subp = subparsers.add_parser("cluster", help="create a clustering plot")
    cluster.sub(subp)

    subp = subparsers.add_parser("pca", help="create a principle component analysis plot")
    pca.sub(subp)

    subp = subparsers.add_parser("annotate", help="annotate a dmr file")
    annotate.sub(subp)

    subp = subparsers.add_parser("average", help="view average methylation of specified regions")
    average.sub(subp)

    args = p.parse_args()

    if not args.subcommand:
        print(p.format_help())
        return

    switch = {
        "call" : call,
        "view" : view,
        "average" : average,
        "index" : index,
        "statistics" : statistics,
        "meta" : meta,
        "cluster" : cluster,
        "pca" : pca,
        "annotate" : annotate,
        "merge" : merge,
        "dmr": dmr,
    }

    # calling the correct submodule
    switch[args.subcommand].run(args)

if __name__ == '__main__':
    run()

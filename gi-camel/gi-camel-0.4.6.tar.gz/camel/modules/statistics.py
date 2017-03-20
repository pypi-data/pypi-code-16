#calculates statistics
import numpy as np
from camel.wrap.sample import Sample

def cast_none(x, type=float):
    if x is None or np.isnan(x):
        x = -1
    return type(x)


def data(filenames):
    for i in filenames:
        sample = Sample(i)
        yield {
            "name" : sample.basename,
            "lanes": cast_none(sample.lane_count, int),
            "duplication_rate": cast_none(sample.duplication_rate),
            "efficiency": cast_none(sample.efficiency),
            "coverage": cast_none(sample.read_coverage),
            "convertion_rate": cast_none(sample.convertion_rate),
            "methylation": cast_none(sample.all_meth),
        }


def out(data):
    #formated print out the data
    print("Sample", "#Track", "Duplication Rate", "Efficiency", "Coverage", "Convertion", "Methylation", sep="\t")
    for d in data:
        print(d["name"], d["lanes"], d["duplication_rate"], d["coverage"], d["convertion_rate"], d["methylation"], sep="\t")


def run(args):
    out(data(args.input))


def sub(parser):
    parser.add_argument('input', nargs='+', help='the input camel call files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='show statistics for camel call files')
    sub(parser)
    args = parser.parse_args()

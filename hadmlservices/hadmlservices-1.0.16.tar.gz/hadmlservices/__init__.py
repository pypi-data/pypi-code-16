import os
import sys
from argparse import ArgumentParser
from hadmlservices import service


def make_parser():
    parser = ArgumentParser()
    parser.add_argument(
        'root_dir',
        help="Root of the directory tree for user_data execution."
    )
    parser.add_argument(
        'input_dir',
        help="Directory containing the source images."
    )
    parser.add_argument(
        'output_dir',
        help="Directory to save the output of model execution."
    )
    parser.add_argument(
        '--model_params',
        default=None,
        help="Model params (if any) combined into a single string"
    )
    return parser

def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    arg_parser = make_parser()
    args = arg_parser.parse_args()
    service.user_data(args.root_dir,
                      args.input_dir,
                      args.output_dir,
                      args.model_params)

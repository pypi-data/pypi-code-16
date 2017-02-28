#!/usr/bin/env python

import argparse

def return_parser():
    parser = argparse.ArgumentParser("Command line tool to print Hello World and demonstrate documenting scripts")
    parser.add_argument("arg0", type=int, help="A needless integer argument for demonstration")
    parser.add_argument("-needless_arg_1", type=int, default=1, help="A needless integer argument for demonstration")
    parser.add_argument("-needless_arg_2", type=str, default='oops', help="A needless string argument for demonstration")
    return parser

if __name__ == '__main__':
    args = return_parser().parse_args()
    print(args.arg0)
    print(args.needless_arg_1)
    print(args.needless_arg_2)
    print('Hello world!')

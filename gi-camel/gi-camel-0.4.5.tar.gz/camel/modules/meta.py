#Access the meta information

import sys
import argparse
import numpy as np
import h5py

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def read(f, name):
    if name not in f["meta"]:
        return
    print(f["meta/" + name][0])


def delete(f, name):
    if name in f["meta"]:
        del f["meta/" + name]
    else:
        print("variable \"", name, "\" not found", sep ="", file=sys.stderr)


def write(f, name, value):
    if isfloat(value):
        value = float(value)
    else:
        value = np.string_(value)

    if not "meta" in f:
        f.create_group("meta")

    if not name in f["meta"]:
        f["meta"].create_dataset(name, data = [value], maxshape=(1,))
    else:
        f["meta"][name][0] = value


def show_all(f):
    for m in f["meta"]:
        print(m, "=", f["meta"][m][0])


def run(args):
    f = h5py.File(args.input) #open the hdf5 file

    if args.name == None:
        show_all(f)
        return

    if args.delete:
        delete(f, args.name)
        return 

    if args.s == None:
        read(f, args.name)
        return

    write(f, args.name, args.s)


def sub(parser):
    parser.add_argument('input', help='the input camel call file')
    parser.add_argument('name', nargs='?', help='the name of the meta information')
    parser.add_argument('-s', default=None, help='write this value as meta information')
    parser.add_argument('--delete', default=False, action='store_true', help='delete the meta information')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Access the meta information.')
    sub(parser)
    args = parser.parse_args()
    run(args)

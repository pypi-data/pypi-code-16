import argparse
import sys
import random
import os


silent = False


def minimize_file(input_file_path, output_file_path, lines):
    if not silent:
        sys.stdout.write("Minimizing file `{}` to {} lines.\n".format(input_file_path, lines))
        sys.stdout.flush()

    counter = 0
    with open(input_file_path) as fp:
        with open(output_file_path, "w") as wp:
            for line in fp:
                wp.write(line)

                counter += 1
                print_progress(counter, lines)
                if counter >= lines:
                    break

    # Force a print of 100% (in the edge case that lines > total line in file.
    print_progress(1, 1)
    sys.stdout.write("\n")


def minimize_file_random(input_file_path, output_file_path, lines):
    if not silent:
        sys.stdout.write("Minimizing file `{}` to {} random lines.\n".format(input_file_path, lines))
        sys.stdout.flush()

    # count number of lines
    total_lines = 0
    with open(input_file_path) as fp:
        for _ in fp:
            total_lines += 1

    if lines > total_lines:
        raise ValueError("File contains {} lines, wanted random sample of {} lines".format(total_lines, lines))

    random_line_nums = set(random.sample(range(total_lines), lines))

    line_num = 0
    counter = 0
    with open(input_file_path) as fp:
        with open(output_file_path, "w") as wp:
            for line in fp:
                if line_num in random_line_nums:
                    wp.write(line)
                    counter += 1
                    print_progress(counter, lines)

                    if counter >= lines:
                        break

                line_num += 1

    # Force a print of 100% (in the edge case that lines > total line in file.
    print_progress(1, 1)
    sys.stdout.write("\n")


def print_progress(count, max_lines):
    if silent:
        return

    percent = count / max_lines
    bars = int(percent * 30)
    sys.stdout.write("\r")
    sys.stdout.write("[{:<30}] {:.2%}".format("=" * bars, percent))
    sys.stdout.flush()


def parse_args():
    parser = argparse.ArgumentParser(description="Input File Minimizer - a text file minimizing CLI tool.")
    parser.add_argument("in_file", help="The file to minimize.")
    parser.add_argument("lines", type=int, help="The number of lines to output.")
    parser.add_argument("-f", dest="file", help="Output file name.")
    parser.add_argument("-C", dest="directory", help="Full path to output the file.")
    parser.add_argument("-r", dest="rnd", help="Randomly skip lines while minimizing.", action="store_true")
    parser.add_argument("--silent", help="Suppress output messages while minimizing.", action="store_true")
    return parser.parse_args()


def process_args(args):
    if args.silent:
        global silent
        silent = True

    if args.directory is None and args.file is None:
        raise ValueError("Must specify an output directory and/or a output file name.")

    # Output directory logic
    output_dir = os.getcwd()
    if args.directory is not None:
        if args.directory.lower() == os.getcwd().lower() and args.file is None:
            raise ValueError("Must specify a output file name if writing to same directory.")
        output_dir = args.directory

    # Input file logic
    file_name = args.in_file
    if args.file is not None:
        file_name = args.file

    input_file_path = args.in_file
    output_file_path = os.path.join(output_dir, file_name)
    lines = args.lines
    random_sample = args.rnd or False

    return input_file_path, output_file_path, lines, random_sample


def main():
    args = parse_args()
    input_file_path, output_file_path, lines, random_sample = process_args(args)
    func = minimize_file_random if random_sample else minimize_file

    func(input_file_path, output_file_path, lines)

    if not silent:
        sys.stdout.write("Minimizing complete.\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

import sys
import re


def print_usage():
    script_name = sys.argv[0]
    print("usage: {} filename".format(script_name))


def exit_with_error(error):
    print(error)
    sys.exit()


def print_red(message):
    print("\033[91m{}\033[0m".format(message))


def print_green(message):
    print("\033[92m{}\033[0m".format(message))


error_pos_re = re.compile(r"(.*?) \(([\d]+):([\d]+)\)")


def parse_acorn_error(error_message):
    match = error_pos_re.search(error_message)

    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))


def get_marker(pos):
    return '-' * (pos - 1) + '^'


def trim_with_margin(string, length, margin=10):
    until = length + margin
    trimmed = string[:until]

    if len(string) > until:
        trimmed += '...'

    return trimmed

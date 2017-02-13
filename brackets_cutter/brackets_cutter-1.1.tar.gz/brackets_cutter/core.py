import re
import argparse


class bcolors:
    WARNING = '\033[93m'


def cut_unclosed_brackets_regexp(input_str):
    return re.compile(r'\([^\)]*$').sub('', input_str)


def cut_unclosed_brackets(input_str):

    opened_bracket = input_str.rfind('(')
    closed_bracket = input_str.rfind(')')

    if (opened_bracket == -1) or (opened_bracket < closed_bracket):
        return input_str
    else:
        return cut_unclosed_brackets(input_str[:opened_bracket])


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('string', help='Input string for my little script.')
    parser.add_argument('-r', '--regexp', action='store_true', help='Cut unclosed brackets using regular expression.')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.regexp:
        print cut_unclosed_brackets_regexp(args.string) + \
              '\n' + bcolors.WARNING + 'This string cut with regular expression~' + bcolors.WARNING
    else:
        print cut_unclosed_brackets(args.string) + \
              '\n' + bcolors.WARNING + 'This string cut without regular expression~' + bcolors.WARNING

if __name__ == '__main__':
    main()

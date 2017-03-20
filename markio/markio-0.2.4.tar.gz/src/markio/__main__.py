import argparse

import sys

from markio.utils import indent


def make_parser():
    def add_params(parser, input=False, debug=False, lang=False):
        if input:
            parser.add_argument('input', help='input Markio file')
        if debug:
            parser.add_argument(
                '--debug', '-d',
                action='store_true',
                help='enable debugging mode'
            )
        if lang:
            parser.add_argument(
                '--lang', '-l',
                type=str,
                help='language of answer key'
            )

    # Creates an argument parser.
    parser = argparse.ArgumentParser('markio')
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid commands',
        help='sub-command help',
    )

    # "markio run" sub-command
    parser_run = subparsers.add_parser('run',
                                       help='run answer key code')
    add_params(parser_run, input=True, debug=True, lang=True)
    parser_run.set_defaults(func=markio_run)

    # "markio test" sub-command
    parser_test = subparsers.add_parser('test',
                                       help='check tests consistency')
    add_params(parser_test, input=True, debug=True, lang=True)
    parser_test.add_argument(
        '--silent', '-s',
        action='store_true',
        help='do not show final test cases expansion'
    )
    parser_test.add_argument(
        '--expansions', '-e',
        type=int,
        help='control the number of expansions'
    )
    parser_test.set_defaults(func=markio_test)

    # "markio src" sub-command
    parser_src = subparsers.add_parser('src',
                                       help='extract source code from files')
    add_params(parser_src, input=True, debug=True, lang=True)
    parser_src.add_argument(
        '--output', '-o',
        type=str,
        help='output file'
    )
    parser_src.set_defaults(func=markio_src)

    return parser


def read_markio(path, debug=False):
    """
    Return a Markio AST from given args.
    """

    import markio
    with open(path) as F:
        try:
            return markio.parse_markio(F)
        except SyntaxError as ex:
            if debug:
                raise
            print('Error in markio file: ' + str(ex))
            sys.exit(1)


def markio_extract_source(args):
    """
    Return source data from given arguments.

    Common functionality of run/src commands.
    """

    md = read_markio(args.input, args.debug)

    # Select language
    if not args.lang and not md.answer_key:
        sys.exit('Error: No answer key defined!')
    elif not args.lang:
        lang, source = next(iter(md.answer_key.items()))
        return md, source, lang.lower()
    else:
        lang = args.lang.lower()
        source = md.answer_key[lang]
        return md, source, lang


def markio_run(args):
    """
    `markio run <file>` command.
    """

    import ejudge
    _, source, lang = markio_extract_source(args)
    ejudge.exec(source, lang=lang)


def markio_src(args):
    """
    `markio src <file>` command.
    """

    _, source, lang = markio_extract_source(args)
    if args.output:
        with open(args.output, 'w', encoding='utf8') as F:
            F.write(source)
    else:
        print(source)


def markio_test(args):
    """
    `markio test <file>` command.
    """

    import ejudge
    md, source, lang = markio_extract_source(args)
    iospec = md.tests
    if args.expansions is not None:
        iospec.expand_inputs(args.expansions)
    results = ejudge.run(source, iospec, lang=lang)

    if results.has_errors:
        for case, expected in zip(results, iospec):
            if case.is_error:
                print('Error executing testcase\n', file=sys.stderr)
                print(indent(expected.source(), 4), file=sys.stderr)
                print('\nMessage\n', file=sys.stderr)
                print(indent(case.get_error_message(), 4), file=sys.stderr)
                sys.exit()

    if args.silent:
        print('Expanded to %s test cases' % len(results))
    else:
        for idx, case in enumerate(results, 1):
            print('Test case %s:' % idx)
            print(indent(case.source(), 4))
            print()
        print('All tests cases were successful!')


def main(args=None):
    args = parser.parse_args(args)

    try:
        func = args.func
    except AttributeError:
        sys.exit('Please select a command. Type `markio -h` for help.')
    else:
        func(args)

parser = make_parser()

# Executed with `python -m markio`
if __name__ == '__main__':
    main()

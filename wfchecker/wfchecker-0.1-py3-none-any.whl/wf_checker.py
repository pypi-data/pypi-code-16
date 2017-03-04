import sys
import json
import tempfile
import subprocess

import utils


def is_javascript(string):
    """
    Tries to guess whether `string` is a javascript program
    """
    if not isinstance(string, str):
        return False

    return any([substr in string for substr in ('=>', 'function', '&&', '||')])


def find_javascript(workflow):
    """
    Searches for javascript fragments in a parsed json structure
    """
    javascript = {}

    for key, value in workflow.items():
        if isinstance(value, dict):
            sub_javascript = find_javascript(value)
            javascript.update(sub_javascript)

        if is_javascript(value):
            javascript[key] = value

    return javascript

def check_fragment(js_fragment):
    """
    Feeds the passed `js_fragment` to a command line js-parser "acorn" and
    returns its response.
    """
    with tempfile.NamedTemporaryFile() as js_file:
        js_file.write(js_code.encode('utf-8'))
        js_file.flush()

        result = subprocess.run(["acorn", "--silent", js_file.name],
                                stderr=subprocess.PIPE)

        return result.stderr.decode('utf-8')


def main():
    if len(sys.argv) < 2:
        utils.print_usage()
        sys.exit()

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as workflow:
            content = workflow.read()
    except IOError as e:
        utils.exit_with_error(str(e))

    try:
        workflow_json = json.loads(content)
    except ValueError as e:
        utils.exit_with_error(
            '"{}" contains invalid json ({})'.format(filename, str(e))
        )

    try:
        result = subprocess.run(["acorn"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        utils.exit_with_error('"acorn" must be installed in order for {} to '
                              'work (npm -g install acorn)'.format(sys.argv[0]))

    javascript_fragments = find_javascript(workflow_json)

    for field, js_code in javascript_fragments.items():
        print('\nChecking field "{}":'.format(field))
        error = check_fragment(js_code)

        if error:
            message, line, col = utils.parse_acorn_error(error)

            utils.print_red(
                "{msg} (line {line}, col {col})".format(
                    msg=message,
                    line=line,
                    col=col
                )
            )
            print(utils.trim_with_margin(js_code, col))
            print(utils.get_marker(col))
        else:
            utils.print_green('OK')


if __name__ == '__main__':
    main()


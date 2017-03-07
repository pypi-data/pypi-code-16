import chalk
import getpass


def get_input(prompt, required=False, secret=False):
    output = None
    _input = getpass.getpass if secret else raw_input

    formatted_prompt = chalk.format_txt('white', prompt, None, ['bold'])
    output = _input(formatted_prompt)
    while not output and required:
        output = _input(formatted_prompt)
    return output
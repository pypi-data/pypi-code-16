import ast
import buzz
import pprintpp


class PydonError(buzz.Buzz):
    pass


def load_string(text):
    with PydonError.handle_errors("Couldn't load data from {}", repr(text)):
        data = ast.literal_eval(text)
    return data


def load_file(filename):
    with open(filename) as text_file:
        return load_string(text_file.read())


def dump_string(data, **pprint_kwargs):
    return pprintpp.pformat(data, **pprint_kwargs)


def dump_file(data, filename, **pprint_kwargs):
    with open(filename, 'w') as text_file:
        text_file.write(dump_string(data, **pprint_kwargs))

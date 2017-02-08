import os


class TestingHelper:
    def __init__(self, basedir):
        self.basedir = basedir

    def get_input_and_output(self, in_file_name, out_file_name):
        in_text = ''
        out_text = ''
        if in_file_name is not None:
            in_file = open(self.basedir + '/data/' + in_file_name, "r")
            in_text = in_file.read()
            in_file.close()

        if out_file_name is not None:
            out_file = open(self.basedir + '/data/' + out_file_name, "r")
            out_text = out_file.read()
            out_file.close()

        return in_text, out_text

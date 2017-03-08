import random
from .words import ADJECTIVES, NOUNS, DELIMITERS


class CodeWordGenerator(object):
    """
    Class to generate a code word pair or code phrase based on the
    **{adjective}{delimiter}{noun}** pattern.  The lists of adjectives, nouns,
    and delimiters may be provided as filenames.
    """
    adjective_list = ADJECTIVES
    noun_list = NOUNS
    delimiter_list = DELIMITERS

    def __init__(self, adjfilename="adjectives.txt", nounfilename="nouns.txt",
                 delimiterfilename="delimiters.txt", *args, **kwargs):
        random.seed()
        self.pattern = kwargs.pop("pattern", "{adjective}{delimiter}{noun}")
        adjfile = kwargs.pop("adjfile", None)
        nounfile = kwargs.pop("nounfile", None)
        delimiterfile = kwargs.pop("delimiterfile", None)

        for (fp, variable) in zip([adjfile, nounfile,
                                   delimiterfile],
                                  ["adjective_list", "noun_list",
                                   "delimiter_list"]):
            try:
                if not fp:
                    continue
                setattr(self, variable,
                        [line.strip() for line in fp.readlines()])
            except IOError:
                pass

        for (filename, variable) in zip([adjfilename, nounfilename,
                                         delimiterfilename],
                                        ["adjective_list", "noun_list",
                                         "delimiter_list"]):
            try:
                if not filename:
                    continue
                with open(filename, "r") as fp:
                    setattr(self, variable,
                            [line.strip() for line in fp.readlines()])
            except IOError:
                pass

    def generate(self, pattern=None):
        """
        Randomly generate a code word pair or code phrase.
        """
        pattern = pattern if pattern else self.pattern
        return pattern.format(
            adjective=random.choice(self.adjective_list),
            delimiter=random.choice(self.delimiter_list),
            noun=random.choice(self.noun_list))

    def _dump(self):
        """
        Simple helper function to dump adjectives and nouns for verification.
        """
        return ["====="] + self.adjective_list + ["====="] + self.noun_list


def _test():
    g = CodeWordGenerator()
    print(g.generate())


if __name__ == '__main__':
    _test()

from markio.marked.parser import MarkedParser
from markio.markio import Markio


def parse_markio(src, **kwargs):
    """
    Parse a Markio source code and return the parsed AST.

    Args:
        src (str or file):
            Marked source code.

    This function assumes the document has the following structure:

        Title
        =====

            Author: Name
            Slug: slug
            Timeout: 1.0
            Language: python


        Short description paragraph.


        Description
        ------------

        Main question description in markdown.


        Example
        -------

            # A simple IoSpec block with an interaction example
            # (indentation makes it valid markdown, but is optional)

            name: <John>
            Hello John!

        Tests
        -----

            # A simple IoSpec block with an interaction example
            # (again, optional indentation)

            name: <Mary>
            Hello Mary!

            @input $name

        Answer Key (python)
        -------------------

            # A block with the answer key source code. You can skip indentation
            # if strict markdown compatibility is not important.

            name = input('name: ')
            print('Hello %s!' % name)

        TLE Answer (python)
        -------------------

            # Used to compute a timeout value for the given language. If you
            # are using this, timeout is interpreted as admissible fraction of
            # the time it took the the TLE to solve the problem. You probably
            # want a number smaller than 1, such as timeout: 0.1

            name = input('name: ')
            print('Hello %s!' % name)


        Placeholder (python)
        --------------------

            # A block of code included in the <textarea> for the given language

            name = input('msg')
            print('sub-string is included here: %s!' % name)
    """

    parser = MarkioParser(src, **kwargs)
    return parser.parse()


class MarkioParser(MarkedParser):
    """
    A Markio-specialized parser.
    """

    def __init__(self, src):
        super().__init__(src, document_class=Markio)
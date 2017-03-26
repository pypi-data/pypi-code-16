from markio.utils import unindent


def test_unindent():
    data = """
    foo
    bar
    """

    assert unindent(data) == '\nfoo\nbar\n'
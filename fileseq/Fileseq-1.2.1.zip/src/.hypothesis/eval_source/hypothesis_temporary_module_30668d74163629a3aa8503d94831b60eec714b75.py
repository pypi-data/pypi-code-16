from hypothesis.utils.conventions import not_set

def accept(f):
    def test_frameset(frange=not_set):
        return f(frange)
    return test_frameset

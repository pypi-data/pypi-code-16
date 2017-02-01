from random import randint

@cookery.action()
def test(subject):
    print("Just a test, passing data from subject.")
    return subject

@cookery.subject("in")
def test():
    return "".join(map(lambda i: randint(0, 1) and i.upper() or i, "fake result"))

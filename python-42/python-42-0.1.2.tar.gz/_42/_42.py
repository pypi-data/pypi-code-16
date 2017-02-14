def _42(fn):
    ''' This decorator comes to the aid of developers in search of an answer.
    Yet, sometimes the answer seems meaningless because the beings who
    instructed it never actually knew what the Question was. So, in this case,
    this decorator returns the answer to the Ultimate Question of Life, the
    Universe and Everything.'''
    def foo():
        try:
            fn()
        except Exception:
            exit(42)

    return foo

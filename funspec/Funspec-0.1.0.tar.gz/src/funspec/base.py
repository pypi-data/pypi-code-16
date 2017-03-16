from funspec.mod import FunspecMod, TestMod


def run_tests(source, funspec, lang=None, num_examples=100, stop_at_error=False,
              sandbox=True):
    """
    Run all tests defined in the given funspec module with the functions defined
    in the input source code.

    Args:
        source (str):
            Source code of the input program.
        funspec (str):
            Source code for the funspec module.
        lang (str):
            The programming language of the input source code.
        num_examples (int):
            Number of examples computed for each answer key by default.
        stop_at_error (bool):
            If True, stop evaluation at the first error and only include this
            error test case in the return :cls:`funspec.Result` object.

    Returns:
        A :cls:`funspec.Result` object.
    """

    funspec_mod = as_funspec_mod(funspec, num_examples)
    test_mod = as_test_mod(source, funspec_mod, lang)

    if sandbox:
        kwargs = dict(
            source=test_mod.source,
            funspec=funspec_mod.source,
            lang=test_mod.lang,
            num_examples=funspec_mod.num_examples,
            stop_at_error=stop_at_error,
            sandbox=False,
        )
        import boxed
        return boxed.run(run_tests, kwargs=kwargs, method='json')
    else:
        return test_mod.run_tests(stop_at_error=stop_at_error)


def as_funspec_mod(funspec, num_examples):
    if isinstance(funspec, str):
        return FunspecMod(funspec, num_examples=num_examples)
    elif isinstance(funspec, FunspecMod):
        return funspec
    else:
        raise TypeError('invalid funspec object: %r' % funspec)


def as_test_mod(source, funspec, lang):
    if isinstance(source, str):
        return TestMod(source, funspec, lang=lang)
    elif isinstance(source, TestMod):
        return source
    else:
        raise TypeError('invalid testmod source object: %r' % funspec)

def hi(some_number, mood='excited', verbose=False):
    """
    Fancy hello world function. :math:`\sum_{i=1}^{10} badDocs*BadlyWrittenCode = frustration`

    :param some_number: (int) Something to return.
    :param mood: (str) A string describing a mood.
    :param verbose: (boolean) Where or not to be a gushing hello world program.
    :return: (int) some_number
    """
    print('hello world! I am %s to be a program.' % mood)
    if verbose:
        print('I am veeeeery %s to meet you' % mood)
    return some_number

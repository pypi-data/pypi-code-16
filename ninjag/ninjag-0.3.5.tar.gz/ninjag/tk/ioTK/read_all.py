def read_all(*files):
    """Read file(s) and return the content

    Args:
        files (str): variable number of file names
    Returns:
        combined content as a string
    """
    output = []
    for f in files:
        with open(f, 'r') as IN:
            output.append(IN.read())
    return "\n".join(output)

def save_text(f_out, *text):
    """Save text to file
    Args:
        f_out (str): output file name
        text (str): variable number of strings of
            file content
    """
    with open(f_out, 'w') as OUT:
        OUT.write("\n".join(text) + "\n")

def prepare_text(text):
    """
    Add quotes if 'str'
    :param text:
    :return:
    """
    if isinstance(text, str):
        if '"' in text:
            return "'" + text.replace("'", "\\'") + "'"
        return '"' + text.replace('"', '\\"') + '"'
    return str(text)

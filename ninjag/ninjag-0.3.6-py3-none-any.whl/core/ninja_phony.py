def ninja_phony(aliases):
    """Return the Ninja phony build section

    Args:
        aliases (list): a list of alias dictionaries
    Returns:
        a string
    """
    return "\n\n".join(
        map(
            lambda x: "build {}: phony {}".format(
                list(x.keys())[0],
                list(x.values())[0]
                ),
            aliases
            )
    )

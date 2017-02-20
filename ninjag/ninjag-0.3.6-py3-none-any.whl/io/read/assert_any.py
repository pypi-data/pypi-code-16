def assert_any(results):
    """
    If any of the results contains
    (True, "") then returns True.
    Otherwise returns False.
    Args:
        results (list): example
            [(True, ""), (False, "Error hint ...")]
    Results:
        True or False
    """
    if any(map(lambda x: x[0], results)):
        return True
    else:
        print("\n\n".join(map(lambda x: x[1], results)))
        exit()

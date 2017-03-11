


def get_remote_address(link):
    """Return the remote address of a link."""
    return link.remote_source.address\
        if link.is_receiver\
        else link.remote_target.address


def _server(server_url: str) -> str:
    server = ''
    if server_url.startswith('http://'):
        server = server_url.split('http://')[1]
    elif server_url.startswith('https://'):
        server = server_url.split('https://')[1]
    return server.rstrip('/')


def full_handle(server_url: str, username: str) -> str:
    """Returns the handle in <username>@<server> format."""
    return username + '@' + _server(server_url)

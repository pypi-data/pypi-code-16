"""Functions for turning markdown blocks into HTML elements."""

def process_block(block):
    """Takes a block of Markdown and returns the correct HTML for that
    block, based on its contents."""

    return "<p>%s</p>" % block

# -*- coding: utf-8 -*-


def assert_popup_redirects(response, url):
    """assert the colorbox response redirects to the right page"""
    if response.status_code != 200:
        raise Exception("colobox Response didn't redirect as expected: Response code was {0} (expected 200)".format(
            response.status_code)
        )

    expected_content = '<script>$.colorbox.close(); window.location="{0}";</script>'.format(url)
    if response.content != expected_content:
        raise Exception("Don't redirect to {0}".format(url))

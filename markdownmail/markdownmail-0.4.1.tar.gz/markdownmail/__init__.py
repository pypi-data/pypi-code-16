import envelopes
import markdown

import markdownmail.styles


class MarkdownMail(envelopes.Envelope):
    def __init__(self, to_addr=None, from_addr=None, subject=None, content=None, css=markdownmail.styles.DEFAULT_STYLE):
        body_content = markdown.markdown(content, output_format="html4", lazy_ol=False)
        embed_css = '<style type="text/css">%(css)s</style>' % {"css": css}

        html = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>%(css)s</head>
<body><div id="content">%(body_content)s</div></body>
</html>""" % {
            "body_content": body_content, "css": embed_css}
        super(MarkdownMail, self).__init__(
            to_addr, from_addr, subject, text_body=content, html_body=html)

    def send(self, smtp_server):
        if issubclass(smtp_server.__class__, NullServer):
            smtp_server.send(self)
        else:
            super(MarkdownMail, self).send(smtp_server)


class NullServer(object):

    def send(self, markdownmail):
        pass


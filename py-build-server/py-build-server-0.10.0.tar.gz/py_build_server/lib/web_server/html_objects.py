def hyperlink(url, name=None):
    return '<a href="{url}">{name}</a>'.format(url=url,
                                               name=url if name is None else name)


def br(lines):
    if isinstance(lines, str):
        return '{}<br>'.format(lines.replace('\n', '<br>'))
    return '<br>'.join(lines)


def h3(text):
    return '<h3>{text}</h3>'.format(text=text)


def base_template(title, body):
    return """
            <html>
                <head>
                    <title>
                        {title}
                    </title>
                </head>
                <body>
                    {body}
                </body>
            </html>
            """.format(title=title, body=''.join(body))

"""
Custom Jinja filters
"""
import re
from jinja2 import Markup
from . import md
from flask import url_for
import humanize
import arrow
from shaft import (init_app,
                   get_config,
                   to_local_datetime,
                   utils)


def format_datetime(dt, format):
    return "" if not dt else arrow.get(dt).format(format)


def format_local_datetime(dt, format):
    return "" if not dt else to_local_datetime(dt).format(format)


def local_datetime(dt):
    f = get_config("DATETIME_DATETIME_FORMAT", "MM/DD/YYYY h:mm a")
    return format_local_datetime(dt, f)


def local_date(dt):
    f = get_config("DATETIME_DATE_FORMAT", "MM/DD/YYYY")
    return format_local_datetime(dt, f)


def local_time_since(dt):
    return to_local_datetime(dt).humanize()

def time_since(dt, timezone="US/Eastern"):
    pass

def nl2br(s):
    """
    {{ s | nl2br }}

    Convert newlines into <p> and <br />s.
    """
    if not isinstance(s, basestring):
        s = str(s)
    s = re.sub(r'\r\n|\r|\n', '\n', s)
    paragraphs = re.split('\n{2,}', s)
    paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />') for p in
                  paragraphs]
    return '\n\n'.join(paragraphs)


def oembed(url, class_=""):
    """
    Create OEmbed link

    {{ url | oembed }}
    :param url:
    :param class_:
    :return:
    """
    o = "<a href=\"{url}\" class=\"oembed {class_}\" ></a>".format(url=url, class_=class_)
    return Markup(o)


def img_src(url, class_="", responsive=False, lazy_load=False, id_=""):
    """
    Create an image src

    {{ xyz.jpg | img_src }}

    :param url:
    :param class_:
    :param responsive:
    :param lazy_load:
    :param id_:
    :return:
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = static_url(url)

    data_src = ""
    if responsive:
        class_ += " responsive"
    if lazy_load:
        data_src = url
        # 1x1 image
        url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        class_ += " lazy"

    img = "<img src=\"{src}\" class=\"{class_}\" id=\"{id_}\" data-src={data_src}>"\
        .format(src=url, class_=class_, id_=id_, data_src=data_src)
    return Markup(img)


def static_url(url):
    """
    {{ url | static }}
    :param url:
    :return:
    """
    return url_for('static', filename=url)


FILTERS = {
    "slug": utils.slugify,  # slug
    "int_comma": humanize.intcomma,  # Transform an int to comma
    "strip_decimal": lambda d: d.split(".")[0],
    "bool_yes": lambda b: "Yes" if b else "No",
    "bool_int": lambda b: 1 if b else 0,
    "markdown": lambda text: Markup(md.html(text)),  # Return a markdown to HTML
    "markdown_toc": md.toc,  # Create a Table of Content of the Markdown
    "nl2br": nl2br,
    "format_local_date": format_local_datetime,  # Require the format to be passed
    "local_date": local_date,
    "local_datetime": local_datetime,
    "local_time_since": local_time_since,
    "time_since": humanize.naturaltime, # To show the time ago: 3 min ago, 2 days ago, 1 year 7 days ago
    "date_since": humanize.naturaldate,  # Show the date ago: Today, yesterday, July 27 (without year in same year), July 15 2014
    "oembed": oembed,
    "img_src": img_src,
    "static": static_url
}

def jinja_helpers(app):
    app.jinja_env.filters.update(FILTERS)

init_app(jinja_helpers)

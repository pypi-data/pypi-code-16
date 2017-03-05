# -*- coding: utf-8 -*-
import sys
import cgi
from time import time
from xml.dom.minidom import parseString
import six.moves.urllib as urllib
from mako.lookup import TemplateLookup
from mako import exceptions
from quickweb import controller



def set_directories(webroot_directory, templates_directories):
    """
    Sets the following configuration directories:
        templates_directories - list of dirs to lookup for templates
    module_directory - directory to keep cached template modules
    """
    global _template_lookup
    global _webroot_directory
    if not '_template_lookup' in globals():
        _template_lookup = None
    if not '_template_lookup' in globals():
        _webroot_directory = None

    _webroot_directory = webroot_directory
    # Template rendering with internationalization support
    _template_lookup = TemplateLookup(directories=templates_directories
                                      , input_encoding='utf-8'
                                      , output_encoding='utf-8'
                                      , encoding_errors='replace'
                                      , strict_undefined=True
                                      , default_filters=['strip_none', 'h']
                                      , imports=['from quickweb.template\
                                            import strip_none, html_lines, quote']
                                     )


def build_simple_form(form_xml):
    dom = parseString(form_xml)
    assert dom.documentElement.tagName == "simpleform"
    new_form = form(role='form', method='post')
    with new_form:
        for element in dom.getElementsByTagName('input'):
            with div(_class="form-group row"):
                with div(_class="col-xs-%i" % int(element.getAttribute('view_size'))):
                    if element.getAttribute('type') == "submit":
                        button(element.getAttribute('label'))
                    else:
                        if element.getAttribute('label'):
                            label(element.getAttribute('label'))
                            kwargs = {'_class': 'form-control'}
                            args = ['type', 'name', 'placeholder']
                            if element.getAttribute('required') == "1":
                                args.append('required')
                            for kw in args:
                                kwargs[kw] = element.getAttribute(kw)
                            input(**kwargs)
    return str(new_form, 'utf-8')


def render(template_name, **kwargs):
    global _template_lookup

    # Prevent from rendering other file types
    if not template_name.endswith('.html'):
        return

    try:
        mytemplate = _template_lookup.get_template(template_name)
    except:
        sys.stderr.write(exceptions.text_error_template().render())
        sys.stderr.write("ERROR: Unable to compile template %s\n" % template_name)
        return

    # Inject herlper functions
    kwargs['build_simple_form'] = build_simple_form

    # Inject custom helper functions
    kwargs["controller_path"] = controller.controller_path()
    kwargs["current_path"] = controller.controller_path()[1]
    kwargs["controller_url"] = controller.controller_url()
    kwargs["controller_session"] = controller.get_session_value

    start_t = time()
    try:
        template_output = [mytemplate.render_unicode(**kwargs)]
    except:
        sys.stderr.write(exceptions.text_error_template().render())
        return exceptions.html_error_template().render()
    stop_t = time()
    if not template_name.endswith('.mail'):
        template_output += '\n<!-- Template %s rendering took %0.3f ms -->\n' % \
                           (template_name, (stop_t - start_t) * 1000.0)
    return template_output


def get_template_def(templatename, defname):
    global _template_lookup
    mytemplate = _template_lookup.get_template(templatename)
    return mytemplate.get_def(defname).render()


"""
   The following are global variables extending the mako templates
"""
# Because the unicode filter returns "None" for None strings
# We want to return '' for those
def strip_none(text):
    if text is None:
        return ''
    else:
        return str(text)


def html_lines(text):
    if text is None:
        return ''
    else:
        text = cgi.escape(text)
        return text.replace('\n', '<br>')


def quote(text):
    return urllib.quote(text.decode('utf-8'), safe='')

from jinja2 import Environment, PackageLoader, select_autoescape
import logging

env = Environment(
    loader=PackageLoader('earlinet_reader', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def create_elpp_html(elpp_object, image_dir):

    template = env.get_template('single_elpp_file.html')
    output_html = template.render({'p': elpp_object, 'image_dir': image_dir})
    output_filename = elpp_object.file_name.replace('.nc', '.html')

    logging.debug('Saving html template in %s.' % output_filename)
    with open(output_filename, 'w') as f:
        f.write(output_html.encode('utf-8'))

    logging.info("Created HTML file %s." % output_filename)

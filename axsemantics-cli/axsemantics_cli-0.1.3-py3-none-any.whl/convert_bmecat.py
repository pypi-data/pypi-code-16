from lxml import etree
import click
import json

from .mapping_helpers import normalize_key

FILENAME = "/home/gentle/Downloads/Bosch.xml"

def strip_ns(tree):
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith('{')
        except AttributeError:
            continue  # node.tag is not a string (node is a comment or similar)
        if has_namespace:
            node.tag = node.tag.split('}', 1)[1]
    return tree


@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def convert_bmecat(input, output):
    feature_keys = {
        'FVALUE': 'value',
        'FDESCR': 'description',
        'FUNIT': 'unit',
    }

    data = strip_ns(etree.parse(input))

    result = []
    for article in data.iterfind('.//ARTICLE'):
        details = {}
        for article_details in article.iterfind('ARTICLE_DETAILS'):
            for detail in article_details.getchildren():
                details[detail.tag] = detail.text
        features = {}
        for feature in article.iterfind('.//FEATURE'):
            fname = normalize_key(feature.find('FNAME').text)
            value = '\n'.join((x.text for x in feature.findall('FVALUE')))

            if fname in features:
                x = 1
                while "{}_{}".format(fname, x) in features:
                    x += 1
                fname = "{}_{}".format(fname, x)
            features[fname] = value
        details['FEATURES'] = features
        result.append(details)
    json.dump(result, output, ensure_ascii=False, indent=2)

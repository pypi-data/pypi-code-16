#!/usr/bin/env python
import click
import codecs
import re
import os
import pandas as pd

from collections import Counter

from nlppln.utils import create_dirs


def load_liwc_dict(dict_file, encoding):

    with codecs.open(dict_file, 'rb', encoding) as f:
        lines = f.readlines()

    liwc_categories = {}
    liwc_dict = {}

    for line in lines:
        # LIWC category
        if line[0].isdigit():
            entry = line.split()
            # remove 0 from strings like 01
            c = str(int(entry[0]))
            liwc_categories[c] = entry[1]
        # word
        elif line[0].isalpha():
            entry = line.split()
            term = entry[0]
            categories = entry[1:]
            liwc_dict[term] = categories
    return liwc_dict, liwc_categories


def liwc_word2re(word):
    word = word.replace('*', '.*')
    return re.compile(r'\b{}\b'.format(word.encode('utf-8')))


@click.command()
@click.argument('liwc_dict', type=click.Path(exists=True))
@click.argument('in_files', nargs=-1, type=click.Path(exists=True))
@click.argument('meta_out', nargs=1, type=click.Path())
@click.option('--encoding', default='utf-8',
              help='Encoding of LIWC dictionary.')
def command(liwc_dict, in_files, meta_out, encoding):
    create_dirs(meta_out)

    liwc, liwc_categories = load_liwc_dict(liwc_dict, encoding)

    result = pd.DataFrame(columns=liwc_categories.values()+['#words'])

    for fi in in_files:
        liwc_count = Counter()

        # make sure all categories have a value in the DataFrame
        for cat in liwc_categories.values():
            liwc_count[cat] = 0

        with codecs.open(fi, encoding='utf-8') as f:
            text = f.read()

        num_words = len(text.split())

        for word, categories in liwc.iteritems():
            regex = liwc_word2re(word)
            matches = re.findall(regex, text)

            if matches:
                print word
                for cat in categories:
                    liwc_count[liwc_categories[cat]] += len(matches)

        fname = os.path.basename(fi)
        result.loc[fname] = pd.Series(liwc_count)
        result.set_value(fname, '#words', num_words)

    result[liwc_categories.values()] = result[liwc_categories.values()].div(result['#words'], axis='index')

    result.to_csv(meta_out, encoding='utf-8')


if __name__ == '__main__':
    command()

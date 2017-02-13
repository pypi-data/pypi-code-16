import json

import listpad
import numpy as np
import tensorflow as tf
import qnd

from .. import classify
from .nlp import *


__all__ = ['def_read_file']


def def_convert_json_example():
    qnd.add_flag('document_length', type=int, default=32)
    qnd.add_flag('sentence_length', type=int, default=64)
    words = def_words()
    get_num_classes = classify.def_num_classes()
    get_num_labels = classify.def_num_labels()

    def convert_json_example(string):
        word_indices = {word: index for index,
                        word in enumerate(words())}

        def convert(string):
            example = json.loads(string.decode())

            document = example['document']
            label = example['label']['binary'
                                     if get_num_classes() == 2 else
                                     'multi']

            return tuple(map(
                lambda x: np.array(x, np.int32),
                [listpad.ListPadder(
                    [qnd.FLAGS.sentence_length, qnd.FLAGS.document_length],
                    NULL_INDEX)
                 .pad([[(word_indices[word]
                         if word in word_indices else
                         UNKNOWN_INDEX)
                        for word in sentence]
                       for sentence in document]),
                 label,
                 len(document)]))

        document, label, document_length = tf.py_func(
            convert,
            [string],
            [tf.int32, tf.int32, tf.int32],
            name="convert_json_example")

        document_length.set_shape([])
        label.set_shape([]
                        if (get_num_labels() is None or
                            get_num_labels() == 1) else
                        [get_num_labels()])

        return (tf.reshape(document,
                           [qnd.FLAGS.document_length,
                            qnd.FLAGS.sentence_length]),
                label)

    return convert_json_example


def def_read_file():
    convert_json_example = def_convert_json_example()

    def read_file(filename_queue):
        key, value = tf.WholeFileReader().read(filename_queue)
        document, label = convert_json_example(value)
        return {'key': key, 'document': document}, {'label': label}

    return read_file

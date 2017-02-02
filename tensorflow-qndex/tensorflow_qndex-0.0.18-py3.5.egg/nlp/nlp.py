import argtyp
import numpy as np
import qnd


__all__ = [
    'NULL_INDEX',
    'UNKNOWN_INDEX',
    'add_char_file_flag',
    'add_word_file_flag',
    'def_word_array'
]


NULL_INDEX = 0
UNKNOWN_INDEX = 1


def add_char_file_flag():
    qnd.add_required_flag('char_file', dest='chars', type=argtyp.file_lines)


def add_word_file_flag():
    qnd.add_required_flag('word_file', dest='words', type=argtyp.file_lines)


def def_word_array():
    qnd.add_flag('word_length', type=int, default=8)
    qnd.add_flag('save_word_array_file')
    add_char_file_flag()
    add_word_file_flag()

    def word_array():
        word_array = np.zeros([len(qnd.FLAGS.words),
                               min(max(len(word) for word in qnd.FLAGS.words),
                                   qnd.FLAGS.word_length)],
                              np.int32)

        for i, word in enumerate(qnd.FLAGS.words):
            for j, char in enumerate(word[:qnd.FLAGS.word_length]):
                word_array[i, j] = (qnd.FLAGS.chars.index(char)
                                    if char in qnd.FLAGS.chars else
                                    UNKNOWN_INDEX)

        word_array[NULL_INDEX, :] = NULL_INDEX
        word_array[UNKNOWN_INDEX, :] = NULL_INDEX
        word_array[UNKNOWN_INDEX, 0] = UNKNOWN_INDEX

        if qnd.FLAGS.save_word_array_file:
            np.savetxt(qnd.FLAGS.save_word_array_file,
                       word_array,
                       fmt='%d',
                       delimiter=',')

        return word_array

    return word_array

import numpy as np
from nltk.tokenize.regexp import WhitespaceTokenizer
import pandas, os, pickle
from tensorgraph.utils import make_one_hot


class CharNumberEncoder(object):

    def __init__(self, data_iterator, tokenizer=WhitespaceTokenizer(), char_map=None, word_len=30, sent_len=200):
        '''
        DESCRIPTIONS:
            This class converts text to numbers for the standard unicode vocabulary
            size.
        PARAMS:
            data_iterator (iterator): iterator to iterates the text strings
            word_len (int): maximum length of the word, any word of length less
                than that will be padded with zeros, any word of length more than
                that will be cut at max word length.
            sent_len (int): maximum number of words in a sentence, any sentence
                with less number of words than that will be padded with zeros,
                any sentence with more words than the max number will be cut at
                the max sentence length.
            char_map (dict): a dictionary for mapping characters to numbers.
        '''
        self.data_iterator = data_iterator
        self.word_len = word_len
        self.sent_len = sent_len
        self.char_map = char_map
        self.tokenizer = tokenizer
        self.char_zero = ' ' # character to be assigned the zero index


    def build_char_map(self):
        char_set = set()
        for paragraph in self.data_iterator:
            for c in str(paragraph):
                char_set.add(c)
        self.char_map = {}
        i = 1
        for c in char_set:
            if c == self.char_zero:
                self.char_map[c] = 0
            else:
                self.char_map[c] = i
                i += 1
        return self.char_map

    def save_params(self, save_path):
        params_dir = os.path.dirname(save_path)
        if not os.path.exists(params_dir):
            os.makedirs(params_dir)
        params = {}
        if self.char_map is None:
            self.build_char_map()
        params['char_map'] = self.char_map
        params['sent_len'] = self.sent_len
        params['word_len'] = self.word_len
        with open(save_path, 'wb') as fout:
            pickle.dump(params, fout)


    def add_char(self, char):
        if char in self.char_map:
            raise Exception('{} already in char_map {}'.format(char, self.char_map))
        self.char_map[char] = len(self.char_map)
        return len(self.char_map)


    def char2num(self, charlen=None, onehot=False):
        '''convert characters in a sentence to numbers limit by charlen
           charlen (int). Convert characters to numbers directly.
        '''
        if self.char_map is None:
            print('..no char_map, building new character map')
            self.build_char_map()
            print('..char_map size = {}'.format(len(self.char_map)))
        sents = []
        for paragraph in self.data_iterator:

            sent_vec = []
            for c in str(paragraph):
                if c not in self.char_map:
                    print('{} not in character map'.format(c))
                else:
                    sent_vec.append(self.char_map[c])

            sents.append(sent_vec)


        if charlen is None:
            sents_lens = [len(sent) for sent in sents]
            mean_len = int(np.mean(sents_lens))
            std_len = int(np.std(sents_lens))
            max_len = mean_len + 2 * std_len
            print('..mean char len = {}, std char len = {}, max char len = {}'.format(mean_len, std_len, max_len))
            charlen = max_len
        else:
            print('..char len = {}'.format(charlen))

        new_sents = []
        for sent_vec in sents:
            if len(sent_vec) > charlen:
                new_sents.append(sent_vec[:charlen])
            else:
                zero_pad = np.zeros(charlen-len(sent_vec)).astype(int)
                sent_vec = sent_vec + list(zero_pad)
                new_sents.append(sent_vec)

        sents = new_sents
        if onehot:
            onehot_sents = []
            for sent in sents:
                onehot_sents += sent

            onehot_sents = make_one_hot(onehot_sents, len(self.char_map))
            sents = onehot_sents.reshape((-1, charlen, len(self.char_map)))

        return np.asarray(sents)



    def make_char_embed(self, onehot=False, reverse_words=False, pad_mode='back'):
        '''DESCRIPTIONS:
               build array vectors of words and sentence, automatically skip non-ascii
               words. First tokenize the sentence into words, then convert each word
               into numbers, then stack together.
           PARAMS:
               reverse_words (bool): reverse the word order in a sentence
               pad_mode (back or front): pad zero at the back or front of sentence
        '''
        if self.char_map is None:
            print('..no char_map, building new character map')
            self.build_char_map()

        print('..total {} characters in char_map'.format(len(self.char_map)))

        sents = []
        char_set = set()
        for paragraph in self.data_iterator:
            word_toks = self.tokenizer.tokenize(str(paragraph))
            word_vecs = []
            for word in word_toks:
                word = word.strip()
                word_vec = []
                for c in word:
                    if c not in self.char_map:
                        print('{} not in character map'.format(c))
                    else:
                        word_vec.append(self.char_map[c])

                if len(word_vec) > 0:
                    word_vecs.append(self.spawn_word_vec(word_vec))
            word_vecs = np.asarray(word_vecs).astype('int16')
            if len(word_vecs) > self.sent_len:
                words = word_vecs[:self.sent_len].astype('int16')
                if reverse_words:
                    words = np.flipud(words)
                sents.append(words)

            else:
                if reverse_words:
                    word_vecs = np.flipud(word_vecs)

                zero_pad = np.zeros((self.sent_len-len(word_vecs), self.word_len))
                if len(word_vecs) > 0:
                    if pad_mode == 'back':
                        sents.append((np.vstack([np.asarray(word_vecs), zero_pad])).astype('int16'))
                    elif pad_mode == 'front':
                        sents.append((np.vstack([zero_pad, np.asarray(word_vecs)])).astype('int16'))
                    else:
                        raise Exception('pad_mode ({}) is neither (front) nor (back)'.format(pad_mode))
                else:
                    sents.append(zero_pad.astype('int16'))

        arr = np.asarray(sents).astype('int16')
        if onehot:
            b, sl, wl = arr.shape
            arr = arr.flatten().astype('int16')
            arr = make_one_hot(arr, len(self.char_map))
            arr = arr.reshape(b, sl, wl, len(self.char_map))
            arr = arr.swapaxes(1, 3)
        return arr


    def spawn_word_vec(self, word_vec):
        '''Convert a word to number vector with max word length, skip non-ascii
           characters
        '''
        if len(word_vec) > self.word_len:
            return word_vec[:self.word_len]
        else:
            word_vec += [0]*(self.word_len-len(word_vec))
        return word_vec



class CatNumberEncoder(object):

    def __init__(self, data_iterator, cat_map=None):

        if not isinstance(data_iterator, pandas.Series):
            try:
                data_iterator = pandas.Series(data_iterator)
            except:
                raise Exception('data_iterator is not pandas.Series instance and cannot be cast to pandas.Seris')
        self.data_iterator = data_iterator
        self.cat_map = cat_map


    def build_cat_map(self, savepath=None):
        '''
        RETURN: table
        '''
        vals = list(self.data_iterator.unique())
        tbl = {}
        idx = 0
        for v in vals:
            if str(v) == 'nan':
                tbl[np.nan] = len(vals)-1 #put nan as the last index
            else:
                tbl[v] = idx
                idx += 1
        self.cat_map = tbl
        print(self.cat_map)
        return self.cat_map


    def make_cat_embed(self):
        '''build array vectors of words and sentence, automatically skip non-ascii
           words.
        '''
        if self.cat_map is None:
            print('..no cat_map, building new character map')
            self.build_cat_map()

        self.data_iterator = self.data_iterator.astype('object').replace(self.cat_map)
        return self.data_iterator.values

if __name__ == '__main__':
    import pandas
    import time
    t1 = time.time()
    df = pandas.read_csv('')
    charnum = CharNumberEncoder(df[''])
    charnum.make_char_embed()
    print(time.time())

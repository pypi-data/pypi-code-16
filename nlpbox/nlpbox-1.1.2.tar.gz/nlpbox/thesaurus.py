
from nltk.corpus import wordnet as wn
from itertools import chain
import nltk
import numpy as np
nltk.download('wordnet')

def thesaurus_str(string):
    toks = str(string).split()
    rstr = []
    for tok in toks:
        synonyms = wn.synsets(tok)
        lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
        if len(lemmas) > 0:
            syn = list(lemmas)[np.random.randint(0,len(lemmas))]
            rstr.append(syn)
        else:
            rstr.append(tok)
    return ' '.join(rstr)


if __name__ == '__main__':
    print(thesaurus_str('hi how are you'))

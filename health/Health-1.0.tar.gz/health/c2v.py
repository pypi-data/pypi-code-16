import gensim
import os

this_dir, this_file = os.path.split(__file__)
path = os.path.join(this_dir, 'data', 'code2vec.p')
code2vec = gensim.models.Word2Vec.load(path)


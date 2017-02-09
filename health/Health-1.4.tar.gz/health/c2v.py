import os
import cPickle

this_dir, this_file = os.path.split(__file__)
path = os.path.join(this_dir, 'data', 'code2vecDict.p')
code2vec = cPickle.load(open(path,'rb'))

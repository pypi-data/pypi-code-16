from baseCodes import *
from getMFCC import *

data_dir = init_data_dir()
print data_dir
sig, rate = wavread('../project/data/test.wav')
print data_dir + 'test.png'
# if_no_create_it(data_dir + 'test.png')
savefig(data_dir + 'test.png', [sig], False)

mfcc_feat = calcMFCC_delta_delta(sig, rate)
print(mfcc_feat.shape)

from baseCodes import *
from getMFCC import *

data_dir = init_data_dir()
sig, rate = wavread(data_dir + '/test.wav')
savefig(data_dir + '/test.png', [sig], False)

mfcc_feat = calcMFCC_delta_delta(sig, rate)
print(mfcc_feat.shape)

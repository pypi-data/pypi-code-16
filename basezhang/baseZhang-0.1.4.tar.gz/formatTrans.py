import os
import pandas
import scipy.io.wavfile as wav
from pydub import AudioSegment
from getMFCC import calcMFCC

SEP=os.sep
def wav2MFCC(dataset_dir='../data/test/dataset',datasetName='dataset'):
    for parent, dirnames, filenames in os.walk(dataset_dir):
        for filename in filenames:
            if '.DS_Store' not in filename and '.doc' not in filename:
                file_path = os.path.join(parent, filename)
                (rate, sig) = wav.read(file_path)
                mfcc_feat = calcMFCC(sig, rate)
                mfcc_feat_path = os.path.dirname(file_path)+SEP+os.path.basename(file_path).split('.')[0]+ '.mfcc'
                mfcc_feat_path=mfcc_feat_path.replace(datasetName,datasetName+'_mfcc')
                if os.path.isdir(mfcc_feat_path):
                    pass
                else:
                    os.makedirs(os.path.dirname(mfcc_feat_path))
                pandas.to_pickle(mfcc_feat, mfcc_feat_path)
    return 0

def mp32Wav(path_to_process='../data/test/dataset',datasetName='dataset',sample_rate=16000):
    count = 0
    for parent, dirnames, filenames in os.walk(path_to_process):
        for filename in filenames:
            if '.mp3' in filename or '.MP3' in filename:
                file_path = os.path.join(parent, filename)
                rate = sample_rate
                count += 1

                print 'processing...NO.%d ' % count + file_path
                file_fromat = file_path[-3:]
                out_path =os.path.dirname(file_path)+SEP+os.path.basename(file_path).split('.')[0]+ '.wav'
                out_path=out_path.replace(datasetName,'mono_wav'+str(rate/1000.0))
                sound = AudioSegment.from_file(file_path, file_fromat)
                new = sound.set_channels(1)
                new = new.set_frame_rate(rate)
                if not os.path.exists(os.path.dirname(out_path)):
                    os.makedirs(os.path.dirname(out_path))
                new.export(out_path, 'wav')
    return 0

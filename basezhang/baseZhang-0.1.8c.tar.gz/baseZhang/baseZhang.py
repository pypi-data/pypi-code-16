# !usr/bin/env python
# coding=gbk
from subprocess import call
from scipy.fftpack import dct
import matplotlib
import pyPdf
from scipy.io.wavfile import read, write
from tqdm import tqdm
matplotlib.use('Agg')
import pylab as pl
import pandas
import scipy.io.wavfile as wav
from pydub import AudioSegment
import subprocess
import math
import numpy
from scipy.fftpack import dct
import matplotlib.pyplot as plt
import pylab
import numpy as np
from numpy.lib import stride_tricks
import os
import wave

INFO = "author:ZHANG Xu-long\nemail:fudan0027zxl@gmail.com\nblog:zhangxulong.site\n"
SEP = os.sep
SHORT_MAX = 32767
EPSILON = 1e-8


def init_data_dir():
    currentPath = os.getcwd()
    projectName = currentPath.split(SEP)[-1]
    if_no_create_it('../data/' + projectName + '/')
    return '../data/' + projectName + '/'


def savefig(filename, figlist, log=True):
    h = 10
    n = len(figlist)
    # peek into instances
    f = figlist[0]
    if len(f.shape) == 1:
        plt.figure()
        for i, f in enumerate(figlist):
            plt.subplot(n, 1, i + 1)
            if len(f.shape) == 1:
                plt.plot(f)
                plt.xlim([0, len(f)])
    elif len(f.shape) == 2:
        Nsmp, dim = figlist[0].shape
        figsize = (h * float(Nsmp) / dim, len(figlist) * h)
        plt.figure(figsize=figsize)
        for i, f in enumerate(figlist):
            plt.subplot(n, 1, i + 1)
            if log:
                plt.imshow(np.log(f.T + EPSILON))
            else:
                plt.imshow(f.T + EPSILON)
    else:
        raise ValueError('Input dimension must < 3.')
    plt.savefig(filename)


def plotMonoWav(mono_wav_path):
    # -*- coding: utf-8 -*-

    # 打开WAV文档
    f = wave.open(mono_wav_path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    # 将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # 绘制波形
    # pl.subplot(211)
    pl.plot(time, wave_data[0])
    # pl.subplot(212)
    # pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0


def plotDuralWav(dural_wav_path):
    # 打开WAV文档
    f = wave.open(dural_wav_path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    # 将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # 绘制波形
    pl.subplot(211)
    pl.plot(time, wave_data[0])
    pl.subplot(212)
    pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0


def wavread(filename):
    fs, x = read(filename)
    x = x.astype(np.float) / SHORT_MAX
    return x, fs


def wavwrite(filename, fs, y):
    ymax = np.max(np.abs(y))
    if ymax < 1.0:
        y = y * SHORT_MAX
    else:
        y = (y / ymax) * SHORT_MAX
    y = y.astype(np.int16)
    write(filename, fs, y)


def print_to_check(print_list=['a', 'b']):
    for print_item in print_list:
        print(print_item)


def if_no_create_it(file_path):
    the_dir = os.path.dirname(file_path)
    if os.path.isdir(the_dir):
        pass
    else:
        os.makedirs(the_dir)


def del_the_file(file_path):
    os.remove(file_path)


def wav2MFCC(dataset_dir='../data/test/dataset', datasetName='dataset'):
    for parent, dirnames, filenames in os.walk(dataset_dir):
        for filename in filenames:
            if '.DS_Store' not in filename and '.doc' not in filename:
                file_path = os.path.join(parent, filename)
                (rate, sig) = wav.read(file_path)
                mfcc_feat = calcMFCC(sig, rate)
                mfcc_feat_path = os.path.dirname(file_path) + SEP + os.path.basename(file_path).split('.')[0] + '.mfcc'
                mfcc_feat_path = mfcc_feat_path.replace(datasetName, datasetName + '_mfcc')
                if os.path.isdir(mfcc_feat_path):
                    pass
                else:
                    os.makedirs(os.path.dirname(mfcc_feat_path))
                pandas.to_pickle(mfcc_feat, mfcc_feat_path)
    return 0


def mp32Wav(path_to_process='../data/test/dataset', datasetName='dataset', sample_rate=16000):
    count = 0
    for parent, dirnames, filenames in os.walk(path_to_process):
        for filename in filenames:
            if '.mp3' in filename or '.MP3' in filename:
                file_path = os.path.join(parent, filename)
                rate = sample_rate
                count += 1

                print 'processing...NO.%d ' % count + file_path
                file_fromat = file_path[-3:]
                out_path = os.path.dirname(file_path) + SEP + os.path.basename(file_path).split('.')[0] + '.wav'
                out_path = out_path.replace(datasetName, 'mono_wav' + str(rate / 1000.0))
                sound = AudioSegment.from_file(file_path, file_fromat)
                new = sound.set_channels(1)
                new = new.set_frame_rate(rate)
                if not os.path.exists(os.path.dirname(out_path)):
                    os.makedirs(os.path.dirname(out_path))
                new.export(out_path, 'wav')
    return 0


def mpeg2wav(mvs_dir='MV'):
    # readme mv title should not have space like that "I Love pytho.mpeg" u can change space to _
    for parent, dirnames, filenames in os.walk(mvs_dir):
        for filename in filenames:
            mv_dir = os.path.join(parent, filename)

            audio_dir = 'audio/' + os.path.splitext(mv_dir)[0] + '.wav'
            if not os.path.exists(os.path.split(audio_dir)[0]):
                os.makedirs(os.path.split(audio_dir)[0])
            command = 'ffmpeg -i ' + mv_dir + ' -ab 160k -ac 2 -ar 44100 -vn ' + audio_dir
            subprocess.call(command, shell=True)

            mono_sound_dir = 'mono/' + audio_dir
            if not os.path.exists(os.path.split(mono_sound_dir)[0]):
                os.makedirs(os.path.split(mono_sound_dir)[0])
            left_audio_dir = 'left_right/' + os.path.splitext(mono_sound_dir)[0] + '_left.wav'
            if not os.path.exists(os.path.split(left_audio_dir)[0]):
                os.makedirs(os.path.split(left_audio_dir)[0])
            right_audio_dir = 'left_right/' + os.path.splitext(mono_sound_dir)[0] + '_right.wav'
            if not os.path.exists(os.path.split(right_audio_dir)[0]):
                os.makedirs(os.path.split(right_audio_dir)[0])
            sound = AudioSegment.from_wav(audio_dir)
            mono = sound.set_channels(1)
            left, right = sound.split_to_mono()
            mono.export(mono_sound_dir, format='wav')
            left.export(left_audio_dir, format='wav')
            right.export(right_audio_dir, format='wav')
    return 0


# coding=utf-8
# 本程序主要有四个函数，它们分别是：
#    audio2frame:将音频转换成帧矩阵
#    deframesignal:对每一帧做一个消除关联的变换
#    spectrum_magnitude:计算每一帧傅立叶变换以后的幅度
#    spectrum_power:计算每一帧傅立叶变换以后的功率谱
#    log_spectrum_power:计算每一帧傅立叶变换以后的对数功率谱
#    pre_emphasis:对原始信号进行预加重处理



def audio2frame(signal, frame_length, frame_step, winfunc=lambda x: numpy.ones((x,))):
    '''将音频信号转化为帧。
	参数含义：
	signal:原始音频型号
	frame_length:每一帧的长度(这里指采样点的长度，即采样频率乘以时间间隔)
	frame_step:相邻帧的间隔（同上定义）
	winfunc:lambda函数，用于生成一个向量
    '''
    signal_length = len(signal)  # 信号总长度
    frame_length = int(round(frame_length))  # 以帧帧时间长度
    frame_step = int(round(frame_step))  # 相邻帧之间的步长
    if signal_length <= frame_length:  # 若信号长度小于一个帧的长度，则帧数定义为1
        frames_num = 1
    else:  # 否则，计算帧的总长度
        frames_num = 1 + int(math.ceil((1.0 * signal_length - frame_length) / frame_step))
    pad_length = int((frames_num - 1) * frame_step + frame_length)  # 所有帧加起来总的铺平后的长度
    zeros = numpy.zeros((pad_length - signal_length,))  # 不够的长度使用0填补，类似于FFT中的扩充数组操作
    pad_signal = numpy.concatenate((signal, zeros))  # 填补后的信号记为pad_signal
    indices = numpy.tile(numpy.arange(0, frame_length), (frames_num, 1)) + numpy.tile(
        numpy.arange(0, frames_num * frame_step, frame_step),
        (frame_length, 1)).T  # 相当于对所有帧的时间点进行抽取，得到frames_num*frame_length长度的矩阵
    indices = numpy.array(indices, dtype=numpy.int32)  # 将indices转化为矩阵
    frames = pad_signal[indices]  # 得到帧信号
    win = numpy.tile(winfunc(frame_length), (frames_num, 1))  # window窗函数，这里默认取1
    return frames * win  # 返回帧信号矩阵


def deframesignal(frames, signal_length, frame_length, frame_step, winfunc=lambda x: numpy.ones((x,))):
    '''定义函数对原信号的每一帧进行变换，应该是为了消除关联性
    参数定义：
    frames:audio2frame函数返回的帧矩阵
    signal_length:信号长度
    frame_length:帧长度
    frame_step:帧间隔
    winfunc:对每一帧加window函数进行分析，默认此处不加window
    '''
    # 对参数进行取整操作
    signal_length = round(signal_length)  # 信号的长度
    frame_length = round(frame_length)  # 帧的长度
    frames_num = numpy.shape(frames)[0]  # 帧的总数
    assert numpy.shape(frames)[1] == frame_length, '"frames"矩阵大小不正确，它的列数应该等于一帧长度'  # 判断frames维度
    indices = numpy.tile(numpy.arange(0, frame_length), (frames_num, 1)) + numpy.tile(
        numpy.arange(0, frames_num * frame_step, frame_step),
        (frame_length, 1)).T  # 相当于对所有帧的时间点进行抽取，得到frames_num*frame_length长度的矩阵
    indices = numpy.array(indices, dtype=numpy.int32)
    pad_length = (frames_num - 1) * frame_step + frame_length  # 铺平后的所有信号
    if signal_length <= 0:
        signal_length = pad_length
    recalc_signal = numpy.zeros((pad_length,))  # 调整后的信号
    window_correction = numpy.zeros((pad_length, 1))  # 窗关联
    win = winfunc(frame_length)
    for i in range(0, frames_num):
        window_correction[indices[i, :]] = window_correction[indices[i, :]] + win + 1e-15  # 表示信号的重叠程度
        recalc_signal[indices[i, :]] = recalc_signal[indices[i, :]] + frames[i, :]  # 原信号加上重叠程度构成调整后的信号
    recalc_signal = recalc_signal / window_correction  # 新的调整后的信号等于调整信号处以每处的重叠程度
    return recalc_signal[0:signal_length]  # 返回该新的调整信号


def spectrum_magnitude(frames, NFFT):
    '''计算每一帧经过FFY变幻以后的频谱的幅度，若frames的大小为N*L,则返回矩阵的大小为N*NFFT
    参数说明：
    frames:即audio2frame函数中的返回值矩阵，帧矩阵
    NFFT:FFT变换的数组大小,如果帧长度小于NFFT，则帧的其余部分用0填充铺满
    '''
    complex_spectrum = numpy.fft.rfft(frames, NFFT)  # 对frames进行FFT变换
    return numpy.absolute(complex_spectrum)  # 返回频谱的幅度值


def spectrum_power(frames, NFFT):
    '''计算每一帧傅立叶变换以后的功率谱
    参数说明：
    frames:audio2frame函数计算出来的帧矩阵
    NFFT:FFT的大小
    '''
    return 1.0 / NFFT * numpy.square(spectrum_magnitude(frames, NFFT))  # 功率谱等于每一点的幅度平方/NFFT


def log_spectrum_power(frames, NFFT, norm=1):
    '''计算每一帧的功率谱的对数形式
    参数说明：
    frames:帧矩阵，即audio2frame返回的矩阵
    NFFT：FFT变换的大小
    norm:范数，即归一化系数
    '''
    spec_power = spectrum_power(frames, NFFT)
    spec_power[spec_power < 1e-30] = 1e-30  # 为了防止出现功率谱等于0，因为0无法取对数
    log_spec_power = 10 * numpy.log10(spec_power)
    if norm:
        return log_spec_power - numpy.max(log_spec_power)
    else:
        return log_spec_power


def pre_emphasis(signal, coefficient=0.95):
    '''对信号进行预加重
    参数含义：
    signal:原始信号
    coefficient:加重系数，默认为0.95
    '''
    return numpy.append(signal[0], signal[1:] - coefficient * signal[:-1])


# 计算每一帧的MFCC系数

# 首先，为了适配版本3.x，需要调整xrange的使用，因为对于版本2.x只能使用range，需要将xrange替换为range
try:
    xrange(1)
except:
    xrange = range


def calcMFCC_delta_delta(signal, samplerate=16000, win_length=0.025, win_step=0.01, cep_num=13, filters_num=26,
                         NFFT=512, low_freq=0, high_freq=None, pre_emphasis_coeff=0.97, cep_lifter=22,
                         appendEnergy=True):
    '''计算13个MFCC+13个一阶微分系数+13个加速系数,一共39个系数
    '''
    feat = calcMFCC(signal, samplerate, win_length, win_step, cep_num, filters_num, NFFT, low_freq, high_freq,
                    pre_emphasis_coeff, cep_lifter, appendEnergy)  # 首先获取13个一般MFCC系数
    result1 = derivate(feat)
    result2 = derivate(result1)
    result3 = numpy.concatenate((feat, result1), axis=1)
    result = numpy.concatenate((result3, result2), axis=1)
    return result


def calcMFCC_delta(signal, samplerate=16000, win_length=0.025, win_step=0.01, cep_num=13, filters_num=26, NFFT=512,
                   low_freq=0, high_freq=None, pre_emphasis_coeff=0.97, cep_lifter=22, appendEnergy=True):
    '''计算13个MFCC+13个一阶微分系数
    '''
    feat = calcMFCC(signal, samplerate, win_length, win_step, cep_num, filters_num, NFFT, low_freq, high_freq,
                    pre_emphasis_coeff, cep_lifter, appendEnergy)  # 首先获取13个一般MFCC系数
    result = derivate(feat)  # 调用derivate函数
    result = numpy.concatenate((feat, result), axis=1)
    return result


def derivate(feat, big_theta=2, cep_num=13):
    '''计算一阶系数或者加速系数的一般变换公式
    参数说明:
    feat:MFCC数组或者一阶系数数组
    big_theta:公式中的大theta，默认取2
    '''
    result = numpy.zeros(feat.shape)  # 结果
    denominator = 0  # 分母
    for theta in numpy.linspace(1, big_theta, big_theta):
        denominator = denominator + theta ** 2
    denominator = denominator * 2  # 计算得到分母的值
    for row in numpy.linspace(0, feat.shape[0] - 1, feat.shape[0]):
        row = int(row)
        tmp = numpy.zeros((cep_num,))
        numerator = numpy.zeros((cep_num,))  # 分子
        for t in numpy.linspace(1, cep_num, cep_num):
            t = int(t)
            a = 0
            b = 0
            s = 0
            for theta in numpy.linspace(1, big_theta, big_theta):
                theta = int(theta)
                if (t + theta) > cep_num:
                    a = 0
                else:

                    a = feat[row][t + theta - 1]
                if (t - theta) < 1:
                    b = 0
                else:
                    b = feat[row][t - theta - 1]
                s += theta * (a - b)
            numerator[t - 1] = s
        tmp = numerator * 1.0 / denominator
        result[row] = tmp
    return result


def calcMFCC(signal, samplerate=16000, win_length=0.025, win_step=0.01, cep_num=13, filters_num=26, NFFT=512,
             low_freq=0, high_freq=None, pre_emphasis_coeff=0.97, cep_lifter=22, appendEnergy=True):
    '''计算13个MFCC系数
    参数含义：
    signal:原始音频信号，一般为.wav格式文件
    samplerate:抽样频率，这里默认为16KHz
    win_length:窗长度，默认即一帧为25ms
    win_step:窗间隔，默认情况下即相邻帧开始时刻之间相隔10ms
    cep_num:倒谱系数的个数，默认为13
    filters_num:滤波器的个数，默认为26
    NFFT:傅立叶变换大小，默认为512
    low_freq:最低频率，默认为0
    high_freq:最高频率
    pre_emphasis_coeff:预加重系数，默认为0.97
    cep_lifter:倒谱的升个数？？
    appendEnergy:是否加上能量，默认加
    '''

    feat, energy = fbank(signal, samplerate, win_length, win_step, filters_num, NFFT, low_freq, high_freq,
                         pre_emphasis_coeff)
    feat = numpy.log(feat)
    feat = dct(feat, type=2, axis=1, norm='ortho')[:, :cep_num]  # 进行离散余弦变换,只取前13个系数
    feat = lifter(feat, cep_lifter)
    if appendEnergy:
        feat[:, 0] = numpy.log(energy)  # 只取2-13个系数，第一个用能量的对数来代替
    return feat


def fbank(signal, samplerate=16000, win_length=0.025, win_step=0.01, filters_num=26, NFFT=512, low_freq=0,
          high_freq=None, pre_emphasis_coeff=0.97):
    '''计算音频信号的MFCC
    参数说明：
    samplerate:采样频率
    win_length:窗长度
    win_step:窗间隔
    filters_num:梅尔滤波器个数
    NFFT:FFT大小
    low_freq:最低频率
    high_freq:最高频率
    pre_emphasis_coeff:预加重系数
    '''

    high_freq = high_freq or samplerate / 2  # 计算音频样本的最大频率
    signal = pre_emphasis(signal, pre_emphasis_coeff)  # 对原始信号进行预加重处理
    frames = audio2frame(signal, win_length * samplerate, win_step * samplerate)  # 得到帧数组
    spec_power = spectrum_power(frames, NFFT)  # 得到每一帧FFT以后的能量谱
    energy = numpy.sum(spec_power, 1)  # 对每一帧的能量谱进行求和
    energy = numpy.where(energy == 0, numpy.finfo(float).eps, energy)  # 对能量为0的地方调整为eps，这样便于进行对数处理
    fb = get_filter_banks(filters_num, NFFT, samplerate, low_freq, high_freq)  # 获得每一个滤波器的频率宽度
    feat = numpy.dot(spec_power, fb.T)  # 对滤波器和能量谱进行点乘
    feat = numpy.where(feat == 0, numpy.finfo(float).eps, feat)  # 同样不能出现0
    return feat, energy


def log_fbank(signal, samplerate=16000, win_length=0.025, win_step=0.01, filters_num=26, NFFT=512, low_freq=0,
              high_freq=None, pre_emphasis_coeff=0.97):
    '''计算对数值
    参数含义：同上
    '''
    feat, energy = fbank(signal, samplerate, win_length, win_step, filters_num, NFFT, low_freq, high_freq,
                         pre_emphasis_coeff)
    return numpy.log(feat)


def ssc(signal, samplerate=16000, win_length=0.025, win_step=0.01, filters_num=26, NFFT=512, low_freq=0, high_freq=None,
        pre_emphasis_coeff=0.97):
    '''
    待补充
    '''
    high_freq = high_freq or samplerate / 2
    signal = pre_emphasis(signal, pre_emphasis_coeff)
    frames = audio2frame(signal, win_length * samplerate, win_step * samplerate)
    spec_power = spectrum_power(frames, NFFT)
    spec_power = numpy.where(spec_power == 0, numpy.finfo(float).eps, spec_power)  # 能量谱
    fb = get_filter_banks(filters_num, NFFT, samplerate, low_freq, high_freq)
    feat = numpy.dot(spec_power, fb.T)  # 计算能量
    R = numpy.tile(numpy.linspace(1, samplerate / 2, numpy.size(spec_power, 1)), (numpy.size(spec_power, 0), 1))
    return numpy.dot(spec_power * R, fb.T) / feat


def hz2mel(hz):
    '''把频率hz转化为梅尔频率
    参数说明：
    hz:频率
    '''
    return 2595 * numpy.log10(1 + hz / 700.0)


def mel2hz(mel):
    '''把梅尔频率转化为hz
    参数说明：
    mel:梅尔频率
    '''
    return 700 * (10 ** (mel / 2595.0) - 1)


def get_filter_banks(filters_num=20, NFFT=512, samplerate=16000, low_freq=0, high_freq=None):
    '''计算梅尔三角间距滤波器，该滤波器在第一个频率和第三个频率处为0，在第二个频率处为1
    参数说明：
    filers_num:滤波器个数
    NFFT:FFT大小
    samplerate:采样频率
    low_freq:最低频率
    high_freq:最高频率
    '''
    # 首先，将频率hz转化为梅尔频率，因为人耳分辨声音的大小与频率并非线性正比，所以化为梅尔频率再线性分隔
    low_mel = hz2mel(low_freq)
    high_mel = hz2mel(high_freq)
    # 需要在low_mel和high_mel之间等间距插入filters_num个点，一共filters_num+2个点
    mel_points = numpy.linspace(low_mel, high_mel, filters_num + 2)
    # 再将梅尔频率转化为hz频率，并且找到对应的hz位置
    hz_points = mel2hz(mel_points)
    # 我们现在需要知道这些hz_points对应到fft中的位置
    bin = numpy.floor((NFFT + 1) * hz_points / samplerate)
    # 接下来建立滤波器的表达式了，每个滤波器在第一个点处和第三个点处均为0，中间为三角形形状
    fbank = numpy.zeros([filters_num, NFFT / 2 + 1])
    for j in xrange(0, filters_num):
        for i in xrange(int(bin[j]), int(bin[j + 1])):
            fbank[j, i] = (i - bin[j]) / (bin[j + 1] - bin[j])
        for i in xrange(int(bin[j + 1]), int(bin[j + 2])):
            fbank[j, i] = (bin[j + 2] - i) / (bin[j + 2] - bin[j + 1])
    return fbank


def lifter(cepstra, L=22):
    '''升倒谱函数
    参数说明：
    cepstra:MFCC系数
    L：升系数，默认为22
    '''
    if L > 0:
        nframes, ncoeff = numpy.shape(cepstra)
        n = numpy.arange(ncoeff)
        lift = 1 + (L / 2) * numpy.sin(numpy.pi * n / L)
        return lift * cepstra
    else:
        return cepstra


# PLOTTING FUNCTIONS for RP_EXTRACT features and Audio Waveforms
def plotmatrix(features, xlabel=None, ylabel=None):
    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    if xlabel: plt.xlabel(xlabel)
    if ylabel: pylab.ylabel(ylabel)
    pylab.show()


def plotrp(features, reshape=True, rows=24, cols=60):
    if reshape:
        features = features.reshape(rows, cols, order='F')
    plotmatrix(features, 'Modulation Frequency Index', 'Frequency Band [Bark]')


def plotssd(features, reshape=True, rows=24, cols=7):
    if reshape:
        features = features.reshape(rows, cols, order='F')

    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    pylab.xticks(range(0, cols), ['mean', 'var', 'skew', 'kurt', 'median', 'min', 'max'])
    pylab.ylabel('Frequency [Bark]')
    pylab.show()


def plotrh(hist, showbpm=True):
    xrange = range(0, hist.shape[0])
    plt.bar(xrange, hist)  # 50, normed=1, facecolor='g', alpha=0.75)

    # plt.ylabel('Probability')
    plt.title('Rhythm Histogram')
    if showbpm:
        mod_freq_res = 1.0 / (2 ** 18 / 44100.0)
        # print type(xrange)
        plotrange = range(1, hist.shape[0] + 1, 5)  # 5 = step
        bpm = np.around(np.array(plotrange) * mod_freq_res * 60.0, 0)
        pylab.xticks(plotrange, bpm)
        plt.xlabel('bpm')
    else:
        plt.xlabel('Mod. Frequency Index')
    plt.show()


def plotmono_waveform(samples, plot_width=6, plot_height=4):
    fig = plt.figure(num=None, figsize=(plot_width, plot_height), dpi=72, facecolor='w', edgecolor='k')

    if len(samples.shape) > 1:
        # if we have more than 1 channel, build the average
        samples_to_plot = samples.copy().mean(axis=1)
    else:
        samples_to_plot = samples

    channel_1 = fig.add_subplot(111)
    channel_1.set_ylabel('Channel 1')
    # channel_1.set_xlim(0,song_length) # todo
    channel_1.set_ylim(-1, 1)

    channel_1.plot(samples_to_plot)

    plt.show();
    plt.clf();


def plotstereo_waveform(samples, plot_width=6, plot_height=5):
    fig = plt.figure(num=None, figsize=(plot_width, plot_height), dpi=72, facecolor='w', edgecolor='k')

    channel_1 = fig.add_subplot(211)
    channel_1.set_ylabel('Channel 1')
    # channel_1.set_xlim(0,song_length) # todo
    channel_1.set_ylim(-1, 1)
    channel_1.plot(samples[:, 0])

    channel_2 = fig.add_subplot(212)
    channel_2.set_ylabel('Channel 2')
    channel_2.set_xlabel('Time (s)')
    channel_2.set_ylim(-1, 1)
    # channel_2.set_xlim(0,song_length) # todo
    channel_2.plot(samples[:, 1])

    plt.show();
    plt.clf();


def plot_waveform(samples, plot_width=6, plot_height=4):
    # mono wave data is either only 1dim in shape or has a 2dim shape with 1 channel only
    if (len(samples.shape) == 1) or (samples.shape[1] == 1):
        print "Plotting Mono"
        plotmono_waveform(samples, plot_width, plot_height)
    else:
        print "Plotting Stereo"
        plotstereo_waveform(samples, plot_width, plot_height)


""" scale frequency axis logarithmically """


def logscale_spec(spec, sr=44100, factor=20.):
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale))

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, scale[i]:], axis=1)
        else:
            newspec[:, i] = np.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.mean(allfreqs[scale[i]:])]
        else:
            freqs += [np.mean(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs


def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.floor(frameSize / 2.0)), sig)
    # cols for windowing
    cols = np.ceil((len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)


def plotstft(samples, samplerate, binsize=2 ** 10, plotpath=None, colormap="jet", ax=None, fig=None, plot_width=6,
             plot_height=4, ignore=False):
    if ignore:
        import warnings

        warnings.filterwarnings('ignore')

    s = stft(samples, binsize)

    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel

    timebins, freqbins = np.shape(ims)

    if ax is None:
        fig, ax = plt.subplots(1, 1, sharey=True, figsize=(plot_width, plot_height))

    # ax.figure(figsize=(15, 7.5))
    cax = ax.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    # cbar = fig.colorbar(cax, ticks=[-1, 0, 1], cax=ax)
    # ax.set_colorbar()

    ax.set_xlabel("time (s)")
    ax.set_ylabel("frequency (hz)")
    ax.set_xlim([0, timebins - 1])
    ax.set_ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    ax.set_xticks(xlocs, ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    ax.set_yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()

    # plt.clf();
    b = ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate]
    return xlocs, b, timebins


def is_R_or_N(user_in_date=2017):  # 判断是否闰年
    # user_in_date = int(input('请输入四位数年份：'))
    # print user_in_date
    value_r_n = user_in_date % 4 == 0 and user_in_date % 100 != 0
    if value_r_n:
        result = str(user_in_date) + '是闰年'
        # print result
    else:
        result = str(user_in_date) + '不是闰年'
        # print result
    return value_r_n


def get_mEnd_days(mEnd=12, is_R_N=True):
    totaldays = 0
    if is_R_N:
        if mEnd == 12:
            totaldays = 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 11:
            totaldays = 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 10:
            totaldays = 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 9:
            totaldays = 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 8:
            totaldays = 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 7:
            totaldays = 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 6:
            totaldays = 31 + 30 + 31 + 29 + 31
        elif mEnd == 5:
            totaldays = 30 + 31 + 29 + 31
        elif mEnd == 4:
            totaldays = 31 + 29 + 31
        elif mEnd == 3:
            totaldays = 29 + 31
        elif mEnd == 2:
            totaldays = 31
        elif mEnd == 1:
            totaldays = 0
    else:
        if mEnd == 12:
            totaldays = 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 11:
            totaldays = 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 10:
            totaldays = 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 9:
            totaldays = 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 8:
            totaldays = 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 7:
            totaldays = 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 6:
            totaldays = 31 + 30 + 31 + 28 + 31
        elif mEnd == 5:
            totaldays = 30 + 31 + 28 + 31
        elif mEnd == 4:
            totaldays = 31 + 28 + 31
        elif mEnd == 3:
            totaldays = 28 + 31
        elif mEnd == 2:
            totaldays = 31
        elif mEnd == 1:
            totaldays = 0

    return totaldays


def get_year_toatal_days(year=2017):
    if is_R_or_N(year):
        total = 366
    else:
        total = 365
    return total


def get_yEnd_yStart_days(yEnd=2017, yStart=1949):
    totaday = 0
    years = range(yStart + 1, yEnd)
    for year_every in years:
        if is_R_or_N(year_every):
            totaday += 366
        else:
            totaday += 365
    return totaday


def countDaysBettweenTwo(dayStart='20150101', dayEnd='20170102'):
    yStart, mStart, dStart = int(dayStart[:4]), int(dayStart[4:6]), int(dayStart[6:8])
    yEnd, mEnd, dEnd = int(dayEnd[:4]), int(dayEnd[4:6]), int(dayEnd[6:8])
    print 'dayStart:', yStart, mStart, dStart
    print 'dayEnd:', yEnd, mEnd, dEnd

    dayPast = dEnd + get_mEnd_days(mEnd, is_R_or_N(yEnd))

    dayLeft = get_year_toatal_days(yStart) - dStart - get_mEnd_days(mStart, is_R_or_N(yStart))

    if yEnd - yStart == 1:
        FinalanswerDay = dayPast + dayLeft
    elif yEnd - yStart < 1:
        FinalanswerDay = dayPast - dStart - get_mEnd_days(mStart, is_R_or_N(yStart))
    else:
        FinalanswerDay = dayPast + dayLeft + get_yEnd_yStart_days(yEnd, yStart)
    return FinalanswerDay


def pdf_link_2_txt(path_pdf='drm20150330-20170310.pdf'):
    PDFFile = open(path_pdf, 'rb')

    PDF = pyPdf.PdfFileReader(PDFFile)
    pages = PDF.getNumPages()
    key = '/Annots'
    uri = '/URI'
    ank = '/A'
    all_link = []
    for page in range(pages):

        pageSliced = PDF.getPage(page)
        pageObject = pageSliced.getObject()

        if pageObject.has_key(key):
            ann = pageObject[key]
            for a in ann:
                u = a.getObject()
                if u[ank].has_key(uri):
                    print u[ank][uri]
                    if 'maomaoChyan' not in u[ank][uri]:
                        if 'channel' not in u[ank][uri]:
                            all_link.append(u[ank][uri])
    print len(all_link)
    print all_link
    print all_link[1]
    out_path = path_pdf.replace('.pdf', '.txt')
    file_txt = open(out_path, 'w')
    for link in all_link:
        file_txt.writelines(link)
        file_txt.writelines('\n')
    file_txt.close()
    return out_path


def download_youtube(link_txt='linkdrm20130701-20150325.txt'):
    txt_file = open(link_txt, 'r')
    links = txt_file.readlines()
    txt_file.close()
    for download_link in tqdm(links):
        # print links
        command = "youtube-dl " + download_link.split('&')[0] + " -c"
        print command
        call(command.split(), shell=False)

    # command = "youtube-dl https://www.youtube.com/watch?v=NG3WygJmiVs -c"
    # call(command.split(), shell=False)
    return 0


def rename_tag(rename_file_dir='toberename', tag='[咻]'):
    for parent, dirnames, filenames in os.walk(rename_file_dir):
        for filename in filenames:
            files_in = os.path.join(parent, filename)
            files_in_name = os.path.basename(files_in)
            files_out = files_in.replace(files_in_name, tag + files_in_name)
            os.rename(files_in, files_out)
    return 0


def modify_markdown(path_to_process='post'):
    for parent, dirnames, filenames in os.walk(path_to_process):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            file_md = open(file_path, 'r')
            all_lines = file_md.readlines()
            file_md.close()
            for line in all_lines:
                if 'category: ' in line:
                    value = line
                    insert_index = all_lines.index(value)
                    all_lines.remove(value)
                    all_lines.insert(insert_index, '- ' + value.split(' ')[1] + '\n')
                    all_lines.insert(insert_index, 'categories:\n')
            file_md = open(file_path, 'w')
            file_md.writelines(all_lines)
    return 0



















# coding=utf-8
from scipy.io.wavfile import read, write
import matplotlib
import os
import wave
import pylab as pl
import numpy as np
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SHORT_MAX = 32767
EPSILON = 1e-8
SEP = os.sep


def init_data_dir():
    currentPath = os.getcwd()
    projectName = currentPath.split(SEP)[-1]
    if_no_create_it('../data/' + projectName+'/')
    return '../data/' + projectName+'/'


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


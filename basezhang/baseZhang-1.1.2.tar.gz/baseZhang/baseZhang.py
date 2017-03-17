# !usr/bin/env python
# coding=gbk
import numpy as np
import os
import matplotlib
from scipy.io.wavfile import read, write
import pip
from subprocess import call

matplotlib.use('Agg')
import matplotlib.pyplot as plt

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


def update_pip_install_packages():
    for dist in pip.get_installed_distributions():
        call("sudo pip install --upgrade " + dist.project_name, shell=True)
    return 0

import os
import os.path as osp
import re
import subprocess


def count_directories(base):
    return len([osp.isdir(osp.join(base, dir_)) for dir_ in os.listdir(base)])


def interactive(result_base):
    print('============= Set Result Base ==============')
    print('0:   set result_base as current directory')

    child_dirs = []
    for dir_ in os.listdir(result_base):
        child_dir = osp.join(result_base, dir_)
        if osp.isdir(child_dir):
            try:
                devnull = open(os.devnull, 'w')
                cmd = 'git log -n 1 --pretty=format:%s_____%ai {}'.format(dir_)
                commit_info = subprocess.check_output([cmd], shell=True, stderr=devnull)
                commit_info = re.sub('[^a-zA-Z0-9, \s, _, \-, :]', '', commit_info)
            except:
                commit_info = None
            print('{}:  {}  n_data={} {}'.format(
                len(child_dirs) + 1,
                dir_,
                count_directories(child_dir),
                commit_info))
            child_dirs.append(dir_)

    var = raw_input("Please enter something: ")
    if int(var) == 0:
        return result_base
    elif 1 <= int(var) <= len(child_dirs):
        return osp.join(result_base, child_dirs[int(var) - 1])
    else:
        raise ValueError('invalid input')


if __name__ == '__main__':
    print interactive('result')

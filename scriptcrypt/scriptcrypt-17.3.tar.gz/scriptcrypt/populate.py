from shutil import copyfile
from os import environ, makedirs, rename, remove
from os.path import exists, dirname


def copyDB(dest):
    if exists(dest):
        new_name = dest + ".old"
        if exists(new_name):
            remove(new_name)
        rename(dest, new_name)
    copyfile(dirname(__file__) + "/data/scriptcrypt.db", dest)


def copyBash():
    copyfile(dirname(__file__) + "/completion/bash/bash_completion",
             environ["HOME"] + "/.bash_completion")
    dirpath = environ["HOME"] + "/.bash_completion.d"
    if not exists(dirpath):
        makedirs(dirpath)
    copyfile(dirname(__file__) + "/completion/bash/scriptcrypt",
             dirpath + "/scriptcrypt")


def copyZsh():
    dirpath = environ["HOME"] + "/.oh-my-zsh/completions"
    if not exists(dirpath):
        makedirs(dirpath)
    copyfile(dirname(__file__) + "/completion/zsh/_scriptcrypt",
             dirpath + "/_scriptcrypt")

import os
import re
import subprocess
import sys

from humanize import naturalsize
from typing import Generator, Tuple

__all__ = ['clean']


def load_files_from_manifest(manifest_file_name: str) -> list:
    print('Parse {}'.format(manifest_file_name))

    with open(manifest_file_name, 'r') as f:
        for line in (l for l in f if l.startswith('DIST') and l.count(' ') > 2):
            yield line.split(' ', 2)[1]


def load_files_from_manifests_folder(folder_name: str) -> list:
    print('Load manifests from {}'.format(folder_name))

    for root, _, files in os.walk(folder_name):
        for manifest in (name for name in files if name == 'Manifest'):
            for file_name in load_files_from_manifest(os.path.join(root, manifest)):
                yield file_name


def portage_env() -> list:
    if not hasattr(portage_env, 'cache'):
        portage_env.cache = subprocess.check_output(['emerge', '--info']).decode('utf-8').split('\n')
    return portage_env.cache


def extract_path(line: str) -> list:
    return line.strip('"').split(' ')


def emerge_value(key: str) -> str:
    try:
        return next(l.split('=')[1] for l in portage_env() if l.startswith('{}='.format(key)))
    except StopIteration:
        return str()


def manifests_folders() -> Generator[None, str, None]:
    regex = re.compile(' *location: (.*)')
    matches = (regex.match(e) for e in portage_env())
    return (m.group(1) for m in matches if m)


def load_file_names() -> list:
    for folder_name in manifests_folders():
        for file_name in load_files_from_manifests_folder(folder_name):
            yield file_name


def distdir() -> str:
    return extract_path(emerge_value('DISTDIR'))[0]


def files_for_clean() -> Generator[None, Tuple[str, int], None]:
    file_names = set(load_file_names())
    distdir_path = distdir()

    for file_name in (f for f in os.listdir(distdir_path) if f not in file_names):
        full_entry_name = os.path.join(distdir_path, file_name)
        if os.path.isfile(full_entry_name):
            yield full_entry_name, os.path.getsize(full_entry_name)


def human_size(size):
    return naturalsize(size, '%.2f')


def clean():
    can_remove = sys.argv.count('--rm')

    total_size = 0
    removed_size = 0
    for file_path, file_size in files_for_clean():
        print('[ {:>10} ] {}'.format(human_size(file_size), file_path))
        total_size += file_size
        if can_remove:
            try:
                os.remove(file_path)
                removed_size += file_size
            except Exception as e:
                print(e)

    print('=' * 120)
    print('[ {:>10} ] Total size'.format(human_size(total_size)))
    print('[ {:>10} ] Removed size'.format(human_size(removed_size)))


if __name__ == '__main__':
    clean()

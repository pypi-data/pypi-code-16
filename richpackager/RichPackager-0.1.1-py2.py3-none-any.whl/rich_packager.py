# coding=utf-8

import argparse
import codecs
import os
import subprocess
import tarfile
import tempfile
import shutil
import json

__author__ = 'lawrentwang'

DIST_CENTER = 'rich_dist_center'


def dir_create(path, base='', if_file=False, exist_ok=True):
    full_path = os.path.abspath(os.path.dirname(os.path.join(base, path))) \
        if if_file else os.path.abspath(os.path.join(base, path))
    if exist_ok:
        if not os.path.exists(full_path):
            os.makedirs(full_path)


class SourceGetSVN(object):
    def __init__(self, vcs_path, local_dir):
        self._svn_path = vcs_path
        self._local_dir = local_dir

        self._revision_number_str = '0'

    def run(self):
        ret = subprocess.check_output(['svn', 'export', self._svn_path], universal_newlines=True,
                                      cwd=self._local_dir)

        for line in ret.strip().split('\n'):
            if line.startswith('Exported revision'):
                self._revision_number_str = line.split('Exported revision')[1].split('.')[0].strip()

    @property
    def version_info(self):
        return self._revision_number_str


class AppPackager(object):
    def __init__(self, vcs_path, python_path):
        self._vcs_path = vcs_path
        self._python_path = python_path

        self._app_dir_name = vcs_path.split('/')[-1]
        self._app_classify = None

        self._version_info = 'None'

        self._include_contents = None
        self._rich_dist_path = None
        self._rich_dist_dir = None

        self._temp_dir = tempfile.mkdtemp()
        self._temp_app_dir_path = os.path.join(self._temp_dir, self._app_dir_name)

        print(self._temp_dir, self._app_dir_name)

    def __getattr__(self, item):
        if item in ['rich_dist_path', 'app_classify']:
            return self.__getattribute__('_' + item)
        else:
            return self.__getattribute__(item)

    def export_source_and_get_info(self):
        obj = SourceGetSVN(self._vcs_path, self._temp_dir)
        obj.run()
        self._version_info = obj.version_info if obj.version_info else self._version_info

    def get_rich_package_info(self):
        rich_package_info_file_path = os.path.join(self._temp_app_dir_path, 'rich_package.json')
        with codecs.open(rich_package_info_file_path, encoding='utf8') as fr:
            rich_package_info = json.load(fr)
        self._include_contents = rich_package_info['include_contents']
        self._app_classify = rich_package_info['app_classify']

        print(self._include_contents, self._app_classify)

    def maintain_dependency(self):
        package_requirements_dir = os.path.join(self._temp_app_dir_path, 'requirements_info')
        dev_package_store_dir = os.path.join(package_requirements_dir,
                                             'package_dev_local')
        pypi_package_store_dir = os.path.join(package_requirements_dir,
                                              'package_pypi_local')

        for cwd in [dev_package_store_dir, pypi_package_store_dir]:
            subprocess.check_call(
                [self._python_path, '-m', 'pip', 'download', '-r', '../requirements_dev.txt'],
                cwd=cwd)

    def add_version_info(self):
        with codecs.open(os.path.join(self._temp_app_dir_path, 'version_info'), 'a', encoding='utf8') as fw:
            fw.write(self._version_info)

    def make_rich_dist(self):
        # 拷贝他数据和依赖文件
        rich_dist_info_item_lst = [self._app_classify, self._app_dir_name, self._version_info]
        rich_dist_dir_lst = [self._app_classify, self._version_info]
        self._rich_dist_dir = os.path.join(DIST_CENTER, *rich_dist_dir_lst)
        if os.path.isdir(self._rich_dist_dir):
            shutil.rmtree(self._rich_dist_dir)
        os.makedirs(self._rich_dist_dir)
        for content in self._include_contents:
            temp_content_path = os.path.join(self._temp_app_dir_path, content)
            if os.path.isdir(temp_content_path):
                shutil.copytree(temp_content_path, os.path.join(self._rich_dist_dir, content))
            if os.path.isfile(temp_content_path):
                shutil.copy(temp_content_path, os.path.join(self._rich_dist_dir, content))

        app_running_dist_name = '_'.join(rich_dist_info_item_lst)
        self._rich_dist_path = os.path.join(DIST_CENTER, self._app_classify,
                                            app_running_dist_name + '.rich')
        with tarfile.open(self._rich_dist_path,
                          'w:gz') as tar_file_obj:
            for dir_name, in_dir_name_lst, in_file_name_lst in os.walk(self._rich_dist_dir):
                for file_item in in_file_name_lst:
                    tar_file_obj.add(os.path.join(dir_name, file_item), arcname=file_item)
                for dir_item in in_dir_name_lst:
                    tar_file_obj.add(os.path.join(dir_name, dir_item), arcname=dir_item)
                break

        print('Making rich dist finished')

    def run(self):
        self.export_source_and_get_info()
        self.get_rich_package_info()
        self.add_version_info()
        self.maintain_dependency()
        self.make_rich_dist()


class AppDeployer(object):
    def __init__(self, dist_path, deploy_path, python_path):
        self._dist_path = os.path.abspath(dist_path)
        self._deploy_path = os.path.abspath(deploy_path)
        self._python_path = python_path

        dir_create(self._deploy_path, exist_ok=True)

    def unpackage_dist(self):
        subprocess.check_call(['tar', '-zxvf', self._dist_path], cwd=self._deploy_path)

    def make_venv(self):
        subprocess.check_call(
            ['virtualenv', 'venv', '-p', self._python_path, '--never-download'], cwd=self._deploy_path)

    def deploy_dist(self):
        subprocess.check_call(
            ['venv/bin/pip', 'install', '-r',
             'requirements_info/requirements_pypi.txt', '-f',
             'requirements_info/package_pypi_local/', '--no-index'], cwd=self._deploy_path)
        subprocess.check_call(
            ['venv/bin/pip', 'install', '-r',
             'requirements_info/requirements_dev_release.txt', '-f',
             'requirements_info/package_dev_local/', '--no-index'], cwd=self._deploy_path)
        subprocess.check_call(
            ['virtualenv', 'venv', '--relocatable'], cwd=self._deploy_path)

        print('Deployment finished.')

    def run(self):
        self.unpackage_dist()
        self.make_venv()
        self.deploy_dist()


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='Rich dist Packager!')
    parse.add_argument('mode', type=str,
                       help='Select run mode.', choices=['p', 'd'])
    parse.add_argument('-p', '--python_path', type=str, required=True,
                       help='Python Interpreter path.')
    parse.add_argument('-l', '--vcs_path', type=str,
                       help='VCS path to fetch.')
    parse.add_argument('-tp', '--dist_path', type=str,
                       help='Dist path.')
    parse.add_argument('-dp', '--deploy_path', type=str,
                       help='Path to deploy dist to.')
    command_args = parse.parse_args()

    if command_args.mode == 'p':
        obj = AppPackager(command_args.vcs_path, command_args.python_path)
        obj.run()
    elif command_args.mode == 'd':
        obj = AppDeployer(command_args.dist_path, command_args.deploy_path, command_args.python_path, )
        obj.run()

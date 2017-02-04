#!/usr/bin/env  python
#-*- coding: utf-8 -*-

"""
使用setupfacory进行打包时，不同的环境需要不同的配置，打包时需要手动点击太麻烦了。
所以开发了基于命令行的自动化打包工具，一条命令自动完成打包工作。
"""

__author__ = 'liu rui'

__version__ = '1.7'

from argparse import ArgumentParser
from enum import Enum, unique
import os
import xml.etree.ElementTree as ET
from io import StringIO
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
import yaml


@unique
class EnvType(Enum):
    stage = 1
    prod = 2

_STAGE = {
    'IM': {
        'DNS': 'lingyi365',
        'IP': '172.18.113.224',
    }}
_PROD = {'IM': {
    'DNS': 'imly365',
    'IP': '211.151.85.100',
}}


def load_config(envType, envDir):
    config_file = os.path.join(envDir, "env", envType.name.lower() + '.yml')
    with open(config_file) as f:
        return yaml.load(f)

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'templates')))


class FileGenerator:

    def __init__(self, fileDir):
        self.__file_dir = fileDir

    def generate(self):
        with StringIO() as f:
            for file in os.scandir(path=self.__file_dir):
                data = None
                if file.is_file():
                    data = dict(name=file.name,
                                path=file.path,
                                source=self.__file_dir,
                                dist_source="",
                                ext=os.path.splitext(file.path)[1][1:],
                                is_file=True)
                else:
                    data = dict(name='*.*',
                                path='%s\\*.*' % file.path,
                                source=file.path,
                                dist_source='\\' + file.name,
                                ext='*',
                                is_file=False,
                                )
                f.write(self._get_file_data(**data))
                f.write('\r\n')
            f.seek(0)
            return f.read()

    def _get_file_data(self, **kw):
        tmp = env.get_template('filedata.j2')
        return tmp.render(kw)


class Generator:

    def __init__(self, file, t, version):
        self.__file = file
        self.__type = t
        self.__version = version
        self.__data = load_config(EnvType[t], os.path.dirname(self.__file))
        self.__setup_file_name = 'setup-%s-%s.exe' % (
            self.__type,  self.__version)
        self.__progame_dir = os.path.join(
            os.path.dirname(self.__file), 'program')
        self.__output_dir = os.path.join(
            os.path.dirname(self.__file), 'dist')

    def _generate_config(self, tmpFile):
        tree = ET.parse(self.__file)
        Generator._generate_version(tree, self.__version)
        Generator._generate_session_data(tree, self.__data)
        Generator._generate_setup_file(tree, self.__setup_file_name)
        Generator._generate_output_folder(tree, self.__output_dir)
        Generator._generate_files(tree, self.__progame_dir)
        tree.write(tmpFile, encoding='iso-8859-1')

    @classmethod
    def _generate_session_data(cls, tree, data):
        for k, v in data["IM"].items():
            ele = tree.find(
                "./SUF7SessionVars/SessionVar[Name='%IM{0}%']".format(k))
            ele.find('Value').text = v

    @classmethod
    def _generate_setup_file(cls, tree, setupFileName):
        setup_file_ele = tree.find(
            './BuildConfigurations/BuildConfig/Filename')
        setup_file_ele.text = setupFileName

    @classmethod
    def _generate_output_folder(cls, tree, outputFolder):
        output_folder_ele = tree.find(
            './BuildConfigurations/BuildConfig/OutputFolder')
        output_folder_ele.text = outputFolder

    @classmethod
    def _generate_version(cls, tree, version):
        version_ele = tree.find(
            "./SUF7SessionVars/SessionVar[Name='%ProductVer%']")
        version_ele.find('Value').text = version

    @classmethod
    def _generate_files(cls, tree, fileDir):
        archive_files_ele = setup_file_ele = tree.find(
            './ArchiveFiles')
        items = FileGenerator(fileDir).generate()
        new_archive_files_ele = ET.fromstring(
            '<ArchiveFiles>' + items + "</ArchiveFiles>")
        new_items = list(x for x in new_archive_files_ele if archive_files_ele.find(
            'FileData[FileName="%s"]' % x.find('FileName').text) is None)
        archive_files_ele.extend(new_items)

    @classmethod
    def _generate_SetIMDNSInfo_file(cls, programDir, data):
        tmp = env.get_template('SetIMDNSInfo.j2')
        content = tmp.render(data)
        with open(os.path.join(programDir, 'SetIMDNSInfo.bat'), 'w') as f:
            f.write(content)

    def generate(self):
        Generator._generate_SetIMDNSInfo_file(self.__progame_dir, self.__data)
        tmp_dir = os.path.join(os.path.dirname(self.__file), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_file_prefix = '-{0}-{1:%y%m%d%H%M%S}'.format(
            self.__version, datetime.now())
        conf_file = os.path.join(tmp_dir, 'tmp%s.suf' % tmp_file_prefix)
        log_file = os.path.join(tmp_dir, 'log%s.txt' % tmp_file_prefix)

        self._generate_config(conf_file)
        ret = os.system('SUFDesign /BUILD "%s" "/STDOUT" >> "%s"' %
                        (conf_file, log_file))

        if ret == 0:
            print('打包成功，安装包文件名为：%s' % self.__setup_file_name)
            os.system('explorer  %s' % self.__output_dir)
        else:
            with open(log_file) as f:
                print(f.read())
            print('打包失败')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("file", help="配置文件")
    parser.add_argument(
        '-t', '--type', choices=['stage', 'prod'], default='stage', help='类型；stage：仿真环境;prod：生产环境；')
    parser.add_argument('-v',  '--version', help='生产的安装包版本')
    parser.add_argument('-V', '--Version', action='version',
                        version='%(prog)s {0}' .format(__version__))
    args = parser.parse_args()

    generator = Generator(args.file, args.type,  args.version)
    generator.generate()

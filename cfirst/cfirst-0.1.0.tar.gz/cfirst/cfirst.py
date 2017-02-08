#coding: utf-8
import os
import sys

help_msg = """学习C语言相关的快捷命令。

Usage:
    cfirst create      创建linux环境
    cfirst exec        进入linux环境
    cfirst remove      删除linux环境
    cfirst start       在linux环境停止后重新启动
    cfirst stop        停止linux环境的运行，删除环境前要先停止环境
    cfirst -h          显示帮助
           --help
"""


def main():
    if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print(help_msg)
        sys.exit(0)
    arg = sys.argv[1]
    if arg == 'create':
        cmd = 'docker run --name cfirstlinux --security-opt seccomp=unconfined -t -i -d -p 8000:8000 registry.cn-hangzhou.aliyuncs.com/coreos/fedora /bin/bash'
    elif arg == 'exec':
        cmd = 'docker exec -it cfirstlinux /bin/bash'
    elif arg == 'remove':
        cmd = 'docker rm cfirstlinux'
    elif arg == 'start':
        cmd = 'docker start cfirstlinux'
    elif arg == 'stop':
        cmd = 'docker stop cfirstlinux'
    else:
        print(help_msg)
        sys.exit(0)
    os.system(cmd)

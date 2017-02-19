#!/usr/bin/env python
import os
import shlex
import subprocess
import time
import sys
import signal
import yaml
from string import Template

stilRun = True


class RunException(Exception):
    pass


# Just to add some colors to terminal
BColors = {
    'HEADER': '\033[95m\033[1m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}


def signal_handler(signal, frame):
    global stilRun
    print("{}exiting{}".format(BColors['WARNING'], BColors['ENDC']))
    stilRun = False


signal.signal(signal.SIGINT, signal_handler)


def use():
    t = Template('''
${BOLD}run [<arguments>]${ENDC}

arguments:
    ${BOLD}-c <config file>${ENDC}: Use specific configuration file, run.yaml in the current folder will be used otherwise
    ${BOLD}-r${ENDC}: Force re-build. Will run build even if ${UNDERLINE}.built.run${ENDC} file is present
    ''')
    print(t.substitute(BColors))


def except_hook(exctype, value, traceback):
    if exctype == RunException:
        print(BColors['FAIL'] + value[0] + BColors['ENDC'])
        use()
        sys.exit(1)
    else:
        sys.__excepthook__(exctype, value, traceback)


sys.excepthook = except_hook


def runCommands(commands, env):
    global stilRun
    maxRepeats = env.get('maxRepeats', 1)
    repeatDelay = env.get('repeatDelay', 0)
    stopOnError = env.get('stopOnError', False)
    curRepeat = 0
    while stilRun and curRepeat < maxRepeats:
        curRepeat += 1
        for command in commands:
            command = Template(command)
            command = command.substitute(env)
            try:
                subprocess.call(shlex.split(command))
            except:
                if stopOnError:
                    raise
                else:
                    e = sys.exc_info()[1]
                    print('{}Error: {}{}'.format(BColors['FAIL'], e, BColors['ENDC']))
        if maxRepeats > curRepeat:
            print('{}Repeating{}{}'.format(BColors['WARNING'], ' in {} sec'.format(repeatDelay) if repeatDelay > 0 else '', BColors['ENDC']))
            if repeatDelay:
                time.sleep(repeatDelay)


def runConfig(config):
    env = dict(os.environ)
    commands = []
    for name, value in config.items():
        if name != 'commands':
            env[name] = value
        else:
            commands = value
    if len(commands) == 0:
        raise RunException('Missing {}commands{} section in configuration file'.format(BColors['BOLD'], BColors['ENDC']))
    runCommands(commands, env)


def main():
    curDir = os.getcwd()
    config = dict()

    # if file exists and `run` was run without rebuild parameter, the project will not be build again
    buildLockFile = os.path.join(curDir, '.built.run')
    needBuild = '-r' in sys.argv
    if not needBuild:
        needBuild = not os.path.exists(buildLockFile)
    print('test {}, {}, ({})'.format(curDir, buildLockFile, needBuild))

    # run configuratoin file
    runConfigFile = os.path.join(curDir, 'run.yaml')
    arg = '-c'
    if arg in sys.argv:
        i = sys.argv.index(arg)
        if len(sys.argv) <= i + 1:
            raise RunException('Missing path of configuration file after -c parameter')
        runConfigFile = sys.argv[i + 1]
    # Load configuration file run.yaml by default
    if not os.path.isfile(runConfigFile):
        raise RunException('The configuration {} should be a YAML configuration file'.format(runConfigFile))
    with open(runConfigFile) as f:
        config = yaml.load(f)
    build = config.get('build')
    if build:
        print('{}BUILD{}'.format(BColors['HEADER'], BColors['ENDC']))
        if needBuild:
            build['stopOnError'] = build.get('stopOnError', True)
            runConfig(build)
            open(buildLockFile, 'a').close()
        else:
            print('{}skipped because of .built.run file{}'.format(BColors['OKGREEN'], BColors['ENDC']))
    run = config.get('run')
    if run:
        print('{}RUN{}'.format(BColors['HEADER'], BColors['ENDC']))
        runConfig(run)
    if not build and not run:
        raise RunException('You should have at least run or build section in {} file'.format(runConfigFile))


if __name__ == '__main__':
    main()

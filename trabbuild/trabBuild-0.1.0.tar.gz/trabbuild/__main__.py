from __future__ import print_function
import os
import re
import sys
import subprocess
import yaml
from distutils.version import LooseVersion

if not os.path.isfile('setup.py'):
    print("No setup.py file found! Aborting..")
    sys.exit()

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
VERSION_REGEX = re.compile(r"(?:(\d+\.(?:\d+\.)*\d+))", re.S)
NAME_REGEX = re.compile(r'[\"\'](.+)[\"\']', re.S)


def get_setup_file():
    with open('setup.py', 'r+') as f:
        return f.readlines()

SETUP_FILE = get_setup_file()


def get_package_info():
    result = dict()
    for line in SETUP_FILE:
        line = line.strip()
        if line.startswith("__version__"):
            version = re.search(VERSION_REGEX, line).group()
            result['version'] = version
        if line.startswith("name=") or line.startswith("name ="):
            name = re.search(NAME_REGEX, line).group()
            result['name'] = name
    return result

PACKAGE_INFO = get_package_info()
PACKAGE_NAME = PACKAGE_INFO['name']
PACKAGE_VERSION = PACKAGE_INFO['version']

print("Welcome to trabBuild!")
print("Ready to update and build package ~ {} ~ {}"
      .format(PACKAGE_NAME, PACKAGE_VERSION))


def get_new_version():
    print("Current version - {}".format(PACKAGE_VERSION))
    new_version = raw_input("Enter new version - $ ") or None
    if new_version is None:
        print("Invalid choice..")
        sys.exit()
    if LooseVersion(new_version) >= LooseVersion(PACKAGE_VERSION):
        return new_version
    else:
        print("Not a valid version number. \n"
              "Please select a version higher than the current one..")
        sys.exit()

NEW_VERSION = get_new_version()


def migrate_setup_file():
    new_setup = []
    for line in SETUP_FILE:
        if line.startswith("__version__"):
            line = re.sub(VERSION_REGEX, NEW_VERSION, line)
            new_setup.append(line)
            continue
        new_setup.append(line)
    return new_setup


def proceed_or_quit():
    confirm = raw_input("Continue?  [y] or n $ ") or 'y'
    if not confirm.lower() == 'y':
        print("Goodbye!")
        sys.exit()

print("This will upgrade your package from v{} to v{}."
      .format(PACKAGE_VERSION, NEW_VERSION))

proceed_or_quit()

NEW_SETUP_FILE = migrate_setup_file()


def write_setup_file(lines):
    with open('setup.py', 'w') as f:
        f.writelines(lines)

write_setup_file(NEW_SETUP_FILE)
print("~ {} ~ package now at version, {}"
      .format(PACKAGE_NAME, NEW_VERSION))


print("Ready to build distros.")
ERRORS = False
proceed_or_quit()


def get_commands_from_yaml(target):
    if not os.path.isfile(target):
        target = os.path.join(SCRIPT_PATH, target)
    with open(target, 'r') as f:
        return yaml.load(f.read())

CUSTOM_COMMANDS_FILE = 'trabbuild.yml'
COMMANDS = get_commands_from_yaml(CUSTOM_COMMANDS_FILE)['builds']

for cmd in COMMANDS:
    try:
        subprocess.call(cmd, shell=True)
    except Exception as e:
        print("Error processing", str(cmd))
        print(e)
        ERRORS = True


print("Ready to upload to twine.")
proceed_or_quit()

response = subprocess.call("twine upload dist/*", shell=True)
if response == 127:
    print("Twine not installed.. Cancelled.")
    ERRORS = True

if ERRORS:
    def revert_version():
        write_setup_file(SETUP_FILE)

    print("Completed with errors..")
    c = raw_input("Would you like to revert back to version {}?  [y] or n"
                  .format(PACKAGE_VERSION)) or 'y'
    if c == 'y':
        revert_version()

print("Goodbye!")

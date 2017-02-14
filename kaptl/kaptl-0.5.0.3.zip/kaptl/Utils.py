try:
    from colorama import Fore, Back, Style, init

    init()
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''


    Fore = Back = Style = ColorFallback()

import difflib
import simplejson as json
import os
import sys
import fnmatch
import pathspec
import subprocess
import re

from Builder import Builder
from exceptions import *


class Utils(object):
    """Utilities and methods used in Kaptl class"""

    @staticmethod
    def path():
        return os.getcwd() + "/.kaptl/kaptl_manifest.json"

    @staticmethod
    def kaptl_ignore_path():
        return os.getcwd() + "/.kaptlignore"

    @staticmethod
    def diff_two_strings(old, new):
        diff = difflib.unified_diff(old, new, fromfile='old', tofile='new', lineterm='', n=2)
        diff = Utils.color_diff(diff)
        joined_diff = '\n'.join(diff)
        return joined_diff

    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is one of "yes" or "no".
        :param default:
        :param question:
        """
        valid = {"yes": "yes", "y": "yes", "ye": "yes",
                 "no": "no", "n": "no"}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while 1:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return default
            elif choice in valid.keys():
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    @staticmethod
    def read_rules_from_file(path):
        try:
            with open(path, "rb") as rules_file:
                file_data = rules_file.read().decode("utf-8-sig")
                pattern = re.compile(r'(import (.+\.kaptl))')
                for line in iter(file_data.splitlines()):
                    for match in pattern.finditer(line):
                        all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
                        for f in all_files:
                            if fnmatch.fnmatch(f, match.group(2)):
                                import_file_data = Utils.read_rules_from_file(f)
                                file_data = file_data.replace(match.group(1), import_file_data)
                return file_data
        except IOError:
            print "ERROR: Couldn't read from a file " + path + ". Check if you have a file named rules.kaptl in " \
                  "your current directory or if a path to your own rules file is correct."
            sys.exit()

    @staticmethod
    def get_kaptl_rules():
        result = {}
        all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in all_files:
            if fnmatch.fnmatch(f, "*.kaptl"):
                file_data = Utils.read_rules_from_file(f)                
                result[f] = file_data
        return result

    @staticmethod
    def build_project():
        builder = Builder()
        try:
            subprocess.call([os.getcwd() + "/NuGet.exe", "restore",
                             os.getcwd() + "/" + Utils.get_solution_file()])
            builder.build(os.getcwd() + "/" + Utils.get_solution_file())
        except MSBuildNotFoundException, e:
            print e.message
            sys.exit()
        except MSBuildFailedException, e:
            print e.message
            sys.exit()

    @staticmethod
    def get_solution_name_from_manifest():
        manifest = Utils.get_manifest_data()
        return manifest.get("solutionName", "MvcApp")

    @staticmethod
    def get_solution_file():
        safeName = Utils.get_solution_name_from_manifest()
        return safeName + ".sln"


    @staticmethod
    def get_stack_info(arguments):
        if arguments["--backend"] is not None:
            backend = [arguments["--backend"]]
            if backend != ["mvc"] and backend != ["sails"]:
                raise WrongStackInfoException("ERROR: Backend framework is specified incorrectly")
        else:
            backend = []

        if arguments["--frontend"] is not None:
            frontend = [arguments["--frontend"]]
            if frontend != ["angular"]:
                raise WrongStackInfoException("ERROR: Frontend framework is specified incorrectly")
        else:
            frontend = []

        if arguments["--backend"] is None and arguments["--frontend"] is None:
            # raise NoStackInfoException("ERROR: Please specify at least one of the stack parts")
            print "Using defaults (Backend: ASP.NET MVC, Frontend: None)"
            backend = ["mvc"]
            frontend = []

        stack = {"backend": backend, "frontend": frontend}

        return stack

    @staticmethod
    def get_kaptl_ignore_spec():
        try:
            if not os.path.isfile(Utils.kaptl_ignore_path()):
                return None
            with open(Utils.kaptl_ignore_path()) as f:
                content = f.readlines()
            return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, content)
        except:
            print "error parsing .kaptlignore", sys.exc_info()[0]
            return None


    @staticmethod
    def get_manifest_data():
        try:
            with open(Utils.path(), 'r') as manifest_file:
                manifest = json.loads(manifest_file.read(), 'utf-8')
                return manifest
        except IOError:
            print "ERROR: Couldn't parse a manifest file. " \
                  "Check if kaptl_manifest.json exists in the directory " \
                  "and is a valid JSON."

    @staticmethod
    def set_manifest_data(key,value):
        try:
            with open(Utils.path(), "r+") as manifest_file:
                manifest = json.loads(manifest_file.read(), 'utf-8')
                existing = manifest.get(key,0)
                new = {key:value}
                if not existing:
                    manifest[key] = value
                elif existing != new[key]:
                    manifest[key] = new[key]
                else:
                    return True
                manifest_file.seek(0)
                manifest_file.truncate()
                json.dump(manifest,manifest_file)
                return True
        except IOError:
            print
            "ERROR: Couldn't parse a manifest file. " \
            "Check if kaptl_manifest.json exists in the directory " \
            "and is a valid JSON."

    @staticmethod
    def get_stack_info_from_manifest():
        manifest = Utils.get_manifest_data()
        stack = manifest.get("stack", None)
        if stack is None:
            return ""
        if stack["backend"] is None:
            stack["backend"] = []
        if stack["frontend"] is None:
            stack["frontend"] = []

        return stack

    @staticmethod
    def manifest(key,default_value=0):
        if os.path.exists(Utils.path()):
            manifest = Utils.get_manifest_data()
            return manifest.get(key,default_value)
        return default_value

    @staticmethod
    def get_id_from_manifest():
        manifest = Utils.get_manifest_data()
        return manifest.get("appId",0)

    @staticmethod
    def check_if_angular_only(stack):
        angular_only = False
        if not stack:
            return False
        if not stack["backend"]:
            if stack["frontend"] == ["angular"]:
                angular_only = True
        return angular_only

    @staticmethod
    def get_readable_stack_string(manifest):
        backend = ""
        frontend = ""
        try:
            if manifest["stack"]:
                if manifest["stack"]["backend"] == ["mvc"]:
                    backend = "ASP.NET MVC"
                elif manifest["stack"]["backend"] == ["sails"]:
                    backend = "Sails.js"
                elif manifest["stack"]["backend"] is None:
                    backend = ""

            if manifest["stack"]["frontend"] == ["angular"]:
                frontend = "AngularJS"
            elif manifest["stack"]["frontend"] is None:
                frontend = ""

            if frontend == "":
                return backend
            elif backend == "":
                return frontend
            else:
                return backend + " + " + frontend

        except KeyError:
            print("Stack does not exist in the manifest file.\nSetting values to None")
            Utils.set_manifest_data("stack", {"backend": "", "frontend": ""})
            return "Empty stack!!!"

    @staticmethod
    def color_diff(diff):
        for line in diff:
            if line.startswith('+'):
                yield Fore.GREEN + line + Fore.RESET
            elif line.startswith('-'):
                yield Fore.RED + line + Fore.RESET
            elif line.startswith('^'):
                yield Fore.BLUE + line + Fore.RESET
            else:
                yield line

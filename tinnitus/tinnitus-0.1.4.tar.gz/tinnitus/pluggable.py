import importlib.util
import os
import threading
from typing import Callable, Any

import sys


class Pluggable(object):

    def __init__(self):

        self.__lock = threading.Lock()
        self.__backends = dict({})
        self.__backend = None
        self.__callback = None

        self.__find_plugins()


    def __add_backend(self, backend: str, module_path: str) -> None:
        with self.__lock:
            spec = importlib.util.spec_from_file_location(backend, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.__backends[backend] = module


    @property
    def backend(self):
        backend = None
        with self.__lock:
            backend = self.__backend
        return backend


    def use_backend(self, backend: str) -> None:
        with self.__lock:
            self.__backend = self.__backends[backend]

            initialized = False

            if hasattr(self.__backend, "initialized"):
                initialized = self.__backend.initialized

            if not initialized:
                self.__backend.init(self.__callback)
                setattr(self.__backend, "initialized", True)


    def set_callback(self, media_end_callback: Callable[[Any], None]) -> None:
        self.__callback = media_end_callback


    def __find_plugins(self):

        plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        include_paths = [plugin_dir]

        with open(os.path.join(plugin_dir, 'include.txt')) as f:
            contents = f.read()

        if contents is not None:
            contents = contents.split("\n")
            include_paths.extend([path for path in contents if path != ""])

        for plugin_path in include_paths:
            for filename in os.listdir(plugin_path):

                absolute_path = os.path.join(plugin_path, filename)
                name, ext = os.path.splitext(filename)

                if ext != '.py':
                    continue

                module = self.__import_relative(name, absolute_path)
                if self.__is_plugin(module):
                    with self.__lock:
                        self.__backends[name] = module


    def __import_relative(self, name, path_to_module):

        spec = importlib.util.spec_from_file_location(name, path_to_module)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module


    def __is_plugin(self, module) -> bool:

        return all([
            hasattr(module, "set_mrl"), callable(getattr(module, "set_mrl")),
            hasattr(module, "init"), callable(getattr(module, "init")),
            hasattr(module, "play"), callable(getattr(module, "play")),
            hasattr(module, "pause"), callable(getattr(module, "pause")),
            hasattr(module, "stop"), callable(getattr(module, "stop"))])


def configure_include_paths():

    argc = len(sys.argv)
    plugin_path = os.path.join(os.path.dirname(__file__), 'plugins')

    if argc == 2:
        if sys.argv[1] == "list":
            contents = ""

            with open(os.path.join(plugin_path, 'include.txt')) as f:
                contents = ''.join([item + "\n" for item in f.read().split("\n") if item != ""])

            print(contents)
            sys.exit(0)

    elif argc == 3:
        if sys.argv[1] == "add":
            try:
                absolute_path = os.path.abspath(sys.argv[2])
            except Exception as e:
                print("Not a valid path!\n"
                      " Check that the path {} exists.".format(sys.argv[2]))
                sys.exit(1)

            with open(os.path.join(plugin_path, 'include.txt'), mode='a') as f:
                f.write(absolute_path + "\n")

            sys.exit(0)

        elif sys.argv[1] == "rem":
            try:
                absolute_path = os.path.abspath(sys.argv[2])
            except Exception as e:
                print("Not a valid path!\n"
                      " Check that the path {} exists.".format(sys.argv[2]))
                sys.exit(1)

            contents = ""
            with open(os.path.join(plugin_path, 'include.txt')) as f:
                contents = f.read().split("\n")

            contents.remove(absolute_path)
            contents = ''.join([item + "\n" for item in contents])

            with open(os.path.join(plugin_path, 'include.txt'), mode='w+') as f:
                f.write(contents)
            sys.exit(0)

    print("Usage:\n"
          "\ttinnitus-include [command] [options]\n"
          "\n"
          "Commands:\n"
          "\tlist     \t- Lists all included plugin paths\n"
          "\tadd PATH \t- Adds PATH to the included plugin paths\n"
          "\trem PATH \t- Adds PATH to the included plugin paths\n"
          "\n"
          "PATH can be relative or absolute.")

import collections
import copy
import difflib
import glob
import io
import itertools
import os
import os.path
import re
import yaml
import yaml.constructor
import yaml.scanner
import yaz

from .log import logger, set_verbose
from .loader import OrderedDictLoader


class Messaging(yaz.BasePlugin):
    """
    Find and evaluate Symfony translation files.
    """
    dirs = ["src/*/Bundle/*/Resources/translations/"]

    def __init__(self):
        logger.debug("translation directories: %s", self.dirs)

    @yaz.task
    def check(self, depth: int = 666, indent: int = 4, verbose: bool = False):
        """
        Find translation files and check them, any required changes will result in an error
        """
        set_verbose(verbose)
        return self.cleanup(changes="fail", duplicate="fail", sync="fail", depth="fail", max_depth=depth, indent_length=indent)

    @yaz.task
    def fix(self, depth: int = 666, indent: int = 4, verbose: bool = False):
        """
        Find translation files and fix them in-line
        """
        set_verbose(verbose)
        return self.cleanup(changes="overwrite", duplicate="first", sync="use-key", depth="join", max_depth=depth, indent_length=indent)

    @yaz.task(changes__choices=["ask", "overwrite", "fail"],
              duplicate__choices=["ask", "first", "last", "fail"],
              sync__choices=["ask", "use-key", "ignore", "fail"],
              depth__choices=["ask", "join", "fail"])
    def cleanup(self, changes="ask", duplicate="ask", sync="ask", depth="ask", max_depth: int = 666, indent_length: int = 4, verbose: bool = False):
        """
        Find translation files and resolve issues using strategies given by the arguments
        """
        set_verbose(verbose)
        for domain, files in self.get_message_files():
            domains = {}

            # Resolve duplicates
            for file in files:
                logger.debug("%s %s", domain, files)
                messages = self.get_messages_from_file(file)
                domains[file] = self.resolve_duplicate_keys(duplicate, messages)

            # Resolve sync
            domains = self.resolve_message_sync(sync, domains)

            # Resolve depth
            for file, messages in domains.items():
                # try:
                messages = self.resolve_message_depth(depth, max_depth, messages)
                # except Exception as error:
                #     raise RuntimeError("{} in file {}".format(error, file))

                # Resolve changes
                self.resolve_changes(changes, file, messages, indent_length)

        return None

    def resolve_duplicate_keys(self, strategy, messages):
        """Given a STRATEGY and a dict with possibly duplicate messages, return a non-duplicate dict

        When there are more than one possible messages,
        the STRATEGY will decide how the duplication is resolved.
        The following STRATEGY options are available:
        - fail: raises a yaz.Error
        - first: chooses the first defined message and ignores any others
        - last: chooses the last defined message and ignores any others
        - ask: lets the user choose the message

        MESSAGES is a dict in the form:
        { translation_key: [first_translation_value, second_translation_value, ...] }

        RETURNS a dict in the form:
        { translation_key: translation_value }
        """
        assert isinstance(strategy, str), type(strategy)
        assert isinstance(messages, dict), type(dict)
        assert all(isinstance(key, str) for key in messages.keys())
        assert all(isinstance(value, list) for value in messages.values())
        assert all(all(isinstance(message, str) for message in value) for value in messages.values())
        if strategy == "fail":
            for key, value in messages.items():
                if len(value) > 1:
                    raise yaz.Error("Translatable \"{}\" has multiple possible values \"{}\"".format(key, value))
            return dict((key, value[0]) for key, value in messages.items())
        elif strategy == "first":
            return dict((key, value[0]) for key, value in messages.items())
        elif strategy == "last":
            return dict((key, value[-1]) for key, value in messages.items())
        elif strategy == "ask":
            for key, value in messages.items():
                if len(value) > 1:
                    raise NotImplementedError("todo: implement duplicate_strategy=\"ask\" strategy")
            return dict((key, value[0]) for key, value in messages.items())

    def resolve_changes(self, strategy, file, messages, indent):
        buffer = io.StringIO()
        yaml.dump(messages, buffer, default_flow_style=False, width=1024 * 5, indent=indent)

        with open(file, "r") as file_handle:
            buffer.seek(0)
            requires_changes = buffer.read() != file_handle.read()

        if requires_changes:
            buffer.seek(0)
            logger.debug("changes detected in file \"%s\"", file)

            if strategy == "fail":
                raise yaz.Error("changes detected in file \"{}\"".format(file))
            if strategy == "overwrite":
                with open(file, "w") as output:
                    for line in buffer.readlines():
                        output.write(line)
            if strategy == "ask":
                with open(file, "r") as file_handle:
                    diff = difflib.context_diff(
                        file_handle.readlines(),
                        buffer.readlines(),
                        "original {}".format(file),
                        "proposed {}".format(file)
                    )
                for line in diff:
                    print(line.rstrip())
                raise NotImplementedError("todo: implement syntax_changes_strategy=\"ask\" strategy")

    def resolve_message_depth(self, strategy, depth, messages):
        assert isinstance(strategy, str), type(strategy)
        assert isinstance(depth, int), type(depth)
        assert isinstance(messages, dict), type(dict)
        assert all(isinstance(key, str) for key in messages.keys())
        assert all(isinstance(value, str) for value in messages.values())
        root = dict()
        for keys, value in sorted(messages.items()):
            keys = keys.split(".", depth)
            layer = root
            prefix = ""
            for key in keys[:-1]:
                if prefix:
                    key = ".".join([prefix, key])
                    prefix = ""

                parent_layer = layer
                try:
                    layer = layer[key]
                except KeyError:
                    layer[key] = layer = dict()

                if isinstance(layer, str):
                    if strategy == "ask":
                        raise NotImplementedError("todo: implement depth_strategy=\"ask\" strategy")

                    if strategy == "join":
                        prefix = key
                        layer = parent_layer
                        continue

                    if strategy == "fail":
                        raise yaz.Error("Conflicting keys when expanding path \"{}\"".format(".".join(keys)))

            key = keys[-1]
            if prefix:
                key = ".".join([prefix, key])
            layer[key] = value

        return root

    def resolve_message_sync(self, strategy, domains):
        assert isinstance(strategy, str), type(strategy)
        assert isinstance(domains, dict), type(domains)
        assert all(isinstance(key, str) for key in domains.keys())
        assert all(isinstance(value, dict) for value in domains.values())
        assert all(all(isinstance(key, str) for key in value.keys()) for value in domains.values())
        assert all(all(isinstance(message, str) for message in value.values()) for value in domains.values())
        all_keys = set()
        all_keys.update(*domains.values())

        if all(len(all_keys) == len(messages) for messages in domains.values()):
            # all domains have all the messages, no need to do anything
            return domains

        if strategy == "ignore":
            return domains

        if strategy == "fail":
            for file, messages in domains.items():
                for key in all_keys.difference(messages.keys()):
                    raise yaz.Error("Translatable \"{}\" is not set in \"{}\"".format(key, file))

        domains = copy.deepcopy(domains)
        if strategy == "use-key":
            for file, messages in domains.items():
                for key in all_keys.difference(messages.keys()):
                    messages[key] = key
                    logger.info("\"use-key\" strategy used to add \"%s\" to \"%s\"", key, file)

        if strategy == "ask":
            raise NotImplementedError("todo: implement duplicate_strategy=\"ask\" strategy")

        return domains

    def get_messages_from_file(self, file):
        """Read messages from a yml file and return a dict

        The returned dictionary contains a single key for every translatable string,
        however, as it is possible to have valid yml with duplicate keys, every key
        points to a list containing one or more translations.

        For example, the the yml file:
            foo.bar: A
            foo:
               bar: B

        Will return:
            {"foo.bar": ["A", "B"]}
        """
        assert isinstance(file, str), type(file)

        def recursion(messages, key, value):
            assert isinstance(messages, dict), type(messages)
            assert isinstance(key, str), type(key)

            if isinstance(value, dict):
                for postfix, value in value.items():
                    assert isinstance(postfix, str), [file, key, postfix, value]
                    recursion(messages, ".".join([key, postfix]), value)
            elif isinstance(value, str):
                messages[key[1:]].append(value)

            return messages

        try:
            with open(file, "r") as file_handle:
                return recursion(collections.defaultdict(list), "", yaml.load(file_handle, OrderedDictLoader))

        except (yaml.scanner.ScannerError, yaml.constructor.ConstructorError) as error:
            raise yaz.Error(error)

    def get_message_files(self):
        """Iterate over available message files grouped by directory and domain"""
        for dir_pattern in self.dirs:
            for dir in glob.glob(dir_pattern):
                files = [re.match(r"^(?P<filename>(?P<domain>\w+)[.](?P<language>\w{2})[.]yml)$", file) for file in sorted(os.listdir(dir))]
                files = [file.groupdict() for file in files if file]
                for domain, files in itertools.groupby(files, lambda file: file["domain"]):
                    yield domain, [os.path.join(dir, file["filename"]) for file in files]
